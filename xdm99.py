#!/usr/bin/env python

# xdm99: A disk manager for TI disk images
#
# Copyright (c) 2015-2019 Ralph Benzinger <xdt99@endlos.net>
#
# This program is part of the TI 99 Cross-Development Tools (xdt99).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import sys
import re
import datetime
import os


VERSION = "3.0.0"


# Utility functions

def ordw(word):
    """word ord"""
    return word[0] << 8 | word[1]


def ordwR(word):
    """reverse word ord"""
    return word[1] << 8 | word[0]


def chrw(word):
    """word chr"""
    return bytes((word >> 8, word & 0xff))


def pad(n, m):
    """return increment to next multiple of m"""
    return -n % m


def used(n, m):
    """integer division rounding up"""
    return (n + m - 1) // m


def xint(s):
    """return hex or decimal value"""
    return int(s.lstrip(">"), 16 if s[:2] == "0x" or s[:1] == ">" else 10)


def tiname(s):
    """create TI filename from local filename"""
    return to_ti(os.path.splitext(os.path.basename(s))[0][:10].upper())


def to_pc(n):
    """escaoe TI filename for PC"""
    return None if n is None else n.replace("/", ".")


def to_ti(n):
    """escape PC name for TI"""
    return None if n is None else n.replace(".", "/")


def sseq(s, i):
    """create string sequence"""
    return s[:-1] + chr(ord(s[-1]) + i)


def writedata(filename, data, encoding=None):
    """write data to file or STDOUT"""
    if encoding is None:
        if filename == "-":
            sys.stdout.buffer.write(data)
        else:
            with open(filename, "wb") as f:
                f.write(data)
    else:
        try:
            if filename == "-":
                sys.stdout.write(data.decode(encoding))
            else:
                with open(filename, "w") as f:
                    f.write(data.decode(encoding))
        except UnicodeDecodeError:
            sys.exit("Bad encoding: " + encoding)


def readdata(filename, data=None, encoding=None):
    """read data from file or STDIN (or return supplied data)"""
    if encoding is None:
        if filename == "-":
            return data or sys.stdin.buffer.read()
        else:
            with open(filename, "rb") as f:
                data = f.read()
                return data
    else:
        try:
            if filename == "-":
                return data or sys.stdin.read().encode(encoding)
            else:
                with open(filename, "r") as f:
                    data = f.read()
                return data.encode(encoding)
        except UnicodeDecodeError:
            sys.exit("Bad encoding: " + encoding)


# Sector-based disk image

class DiskError(Exception):
    pass


class Disk:
    """sector-based TI disk image file"""

    bytes_per_sector = 256
    default_sectors_per_track = 9
    default_tracks = 40
    max_sectors = 1600
    blank_byte = b"\xe5"

    def __init__(self, image):
        if len(image) < 2 * Disk.bytes_per_sector:
            raise DiskError("Invalid disk image")
        self.image = image
        self.read_sectors = []
        self.warnings = {}
        # meta data
        sector_0 = self.get_sector(0)
        if sector_0[0] == 0x00 and sector_0[21:23] == b"\x00\xfe":
            raise DiskError("Track dump images not supported")
        self.name = sector_0[:0x0a].decode()
        self.total_sectors = ordw(sector_0[0x0a:0x0c])
        self.sectors_per_track = sector_0[0x0c]
        self.dsk_id = sector_0[0x0d:0x10]
        self.protected = sector_0[0x10]
        self.tracks_per_side = sector_0[0x11]
        self.sides = sector_0[0x12]
        self.density = sector_0[0x13]
        self.alloc_bitmap = sector_0[0x38:]
        # derived values and sanity checks
        if self.dsk_id != b"DSK":
            self.warn("Disk image not initialized", "image")
        if len(self.image) < self.total_sectors * Disk.bytes_per_sector:
            self.warn("Disk image truncated", "image")
        self.check_geometry()
        self.used_sectors = 0
        try:
            for i in range(used(self.total_sectors, 8)):
                self.used_sectors += bin(self.alloc_bitmap[i]).count("1")
        except IndexError:
            self.warn("Allocation map corrupted", "alloc")
        self.catalog = {}
        self.init_catalog()
        self.check_allocation()

    def check_geometry(self):
        """check geometry against sector count"""
        if self.total_sectors != self.sides * self.tracks_per_side * self.sectors_per_track:
            self.warn("Sector count does not match disk geometry", "geom")
        if self.total_sectors % 8 != 0:
            self.warn("Sector count is not multiple of 8", "geom")

    def rename(self, name):
        """rename disk"""
        self.name = name
        if len(self.name.encode()) > 10:
            raise DiskError("Encoded name is too long")
        self.image = self.name.encode() + b" " * (10 - len(self.name)) + self.image[0x0a:]

    def init_catalog(self):
        """read all files from disk"""
        sector_1 = self.get_sector(1)
        sector_count = 0
        for i in range(0, Disk.bytes_per_sector, 2):
            # get file descriptor
            fd_index = ordw(sector_1[i:i + 2])
            if fd_index == 0:
                break
            try:
                fd_sector = self.get_sector(fd_index, b"FDR#%d" % fd_index)
            except IndexError:
                self.warn("File descriptor index corrupted")
                continue
            fd = FileDescriptor(sector=fd_sector)
            # get file contents
            data, error = self.read_file(fd.name, fd.total_sectors, fd.clusters)
            if error:
                fd.error = True
            self.catalog[fd.name] = File(fd=fd, data=data)
            sector_count += fd.total_sectors + 1
        # consistency check
        if sector_count != self.used_sectors - 2:
            self.warn("Used sector mismatch: found {} file sectors, expected {}".format(
                    sector_count, self.used_sectors - 2))

    def read_file(self, name, sectors, clusters):
        """read file contents based on FDR cluster data"""
        data = b""
        offset = -1
        error = False
        for p in range(0, len(clusters) - 2, 3):
            start = clusters[p] | (clusters[p + 1] & 0x0f) << 8
            if start == 0:
                break
            prev, offset = offset, clusters[p + 1] >> 4 | clusters[p + 2] << 4
            for i in range(offset - prev):
                try:
                    data += self.get_sector(start + i, name)
                except IndexError:
                    self.warn("%s: File contents corrupted" % name)
                    error = True
                    continue
        if len(data) != sectors * Disk.bytes_per_sector:
            self.warn("{}: File size mismatch: found {} bytes, expected {}".format(
                name, len(data), sectors * Disk.bytes_per_sector))
            error = True
        return data, error

    def glob_files(self, patterns):
        """return list of filenames matching glob pattern"""
        wildcards = [p for p in patterns if re.search("[?*]", p)]
        glob_re = "|".join([re.escape(p).replace("\*", ".*").replace("\?", ".")
                            for p in wildcards]) + "$"
        matches = [name for name in self.catalog if re.match(glob_re, name)]
        plains = [p for p in patterns if p not in wildcards]
        return matches + plains

    def rebuild_disk(self):
        """rebuild disk metadata after changes to file catalog"""
        required_sectors = sum([self.catalog[n].fd.total_sectors for n in self.catalog])
        # preferred start at sector >22
        first_free = next_free = min(max(2 + len(self.catalog), 0x22), self.total_sectors - required_sectors)
        if first_free < 2 + len(self.catalog):
            raise DiskError("Disk full, lacking {} sectors".format(2 + len(self.catalog) - first_free))

        index= 2
        sector_1 = b""
        for n in sorted(self.catalog):
            file_ = self.catalog[n]
            # put file data into single cluster
            data = file_.data
            for j in range(file_.fd.total_sectors):
                self.set_sector(next_free + j,
                                data[Disk.bytes_per_sector * j:Disk.bytes_per_sector * (j + 1)])
            # build file descriptor
            start, offset = (next_free, file_.fd.total_sectors - 1) if file_.fd.total_sectors > 0 else (0, 0)
            file_.fd.clusters = (bytes((start & 0xff, start >> 8 | (offset & 0xf) << 4, offset >> 4)) +
                                 bytes(Disk.bytes_per_sector - 0x1c - 3))
            self.set_sector(index, file_.fd.get_sector())
            # update FDR index in sector 1
            sector_1 += chrw(index)
            index, next_free = index + 1, next_free + file_.fd.total_sectors
        sector_1 += bytes(Disk.bytes_per_sector - len(sector_1))
        self.set_sector(1, sector_1)
        # update allocation bitmap in sector 0 (used: 0..i-1, ff..nf-1)
        assert 0 < index <= first_free <= next_free
        mask = int("1" * (next_free - first_free) +
                   "0" * (first_free - index) + "1" * index, 2)  # bitmap as bits, parsed into (very large) int
        bytes_ = []
        for i in range(self.total_sectors // 8):  # byte-ize int from the tail
            bytes_.append(bytes((mask & 0xff,)))
            mask >>= 8
        bytes_.append(b"\xff" * (Disk.bytes_per_sector - 0x38 - len(bytes_)))
        bitmap = b"".join(bytes_)
        self.alloc_bitmap = bitmap
        sector_0 = self.get_sector(0)
        self.set_sector(0, sector_0[:0x38] + bitmap)

    @staticmethod
    def extend_sectors(image, new_size):
        """increase total number of sectors and clear alloc map (for xvm99)"""
        current = ordw(image[0x0a:0x0c])
        if not current <= new_size <= Disk.max_sectors:
            raise DiskError("Invalid size %d for sector increase" % new_size)
        if current % 8 != 0:
            raise DiskError("Unsupported total sector count of %d" % current)
        bitmap = (image[0x38:0x38 + current // 8] +
                  b"\xff" * (Disk.bytes_per_sector - 0x38 - current // 8))
        return image[:0x0a] + chrw(new_size) + image[0x0c:0x38] + bitmap + image[0x100:]

    @staticmethod
    def trim_sectors(image):
        """shrink image to actually existing sectors"""
        total_sectors = ordw(image[0x0a:0x0c])
        return image[:total_sectors * Disk.bytes_per_sector]

    def get_sector(self, n, context=None):
        """retrieve sector from image"""
        if n > 0 and n >= self.total_sectors:
            raise IndexError("Invalid sector number")
        if context:
            self.read_sectors.append((n, context))
        offset = n * Disk.bytes_per_sector
        return self.image[offset:offset + Disk.bytes_per_sector]

    def set_sector(self, n, data):
        """write sector to image"""
        if n > self.total_sectors:
            raise IndexError("Invalid sector number")
        if len(data) != Disk.bytes_per_sector:
            raise ValueError(
                "Invalid data for sector %d: found %d bytes, expected %d" % (
                    n, len(data), Disk.bytes_per_sector))
        offset = n * Disk.bytes_per_sector
        self.image = self.image[:offset] + data + self.image[offset + Disk.bytes_per_sector:]

    def get_file(self, name):
        """get File object from disk catalog"""
        if name not in self.catalog:
            raise DiskError(f"File {name} not found")
        return self.catalog[name]

    def add_file(self, file_):
        """add or update File object in image"""
        self.catalog[file_.fd.name] = file_
        self.rebuild_disk()

    def remove_file(self, name):
        """remove file from image"""
        try:
            del self.catalog[name]
            self.rebuild_disk()
        except IndexError:
            raise DiskError(f"File {name} not found")

    def rename_files(self, names):
        """rename files in image"""
        # dry-run first
        try:
            for old, new in names:
                if old not in self.catalog:
                    raise DiskError(f"File {old} not found")
                if new in self.catalog:
                    raise DiskError(f"File {new} already exists")
        except ValueError:
            raise DiskError("Bad renaming argument")
        # actual renaming
        for old, new in names:
            self.catalog[old].fd.name = new
            self.catalog[new] = self.catalog[old]
            del self.catalog[old]
        self.rebuild_disk()

    def protect_file(self, name):
        """toggle protection for given file"""
        try:
            file_ = self.catalog[name]
        except KeyError:
            raise DiskError(f"File {name} not found")
        file_.fd.toggle_protection()
        self.rebuild_disk()

    def check_allocation(self):
        """check sector allocation for consistency"""
        reads = {n: [] for n in range(self.total_sectors)}
        allocated = []
        for i in range(used(self.total_sectors, 8)):
            b = self.alloc_bitmap[i]
            for j in range(8):
                allocated.append(b & 1 << j != 0)
        # unallocated sectors
        for n, context in self.read_sectors:
            reads[n].append(context)
            if context and not allocated[n]:
                self.warn(f"{context}: Used sector {n} not allocated")
                file_ = self.catalog.get(context)
                if file_:
                    file_.fd.error = True
        # sectors allocated to multiple files
        for n, files in [(i, reads[i]) for i in reads if len(reads[i]) > 1]:
            self.warn(f"Sector {n} claimed by multiple files: {'/'.join(files)}")
            for name in files:
                file_ = self.catalog.get(name)
                if file_:
                    file_.fd.error = True

    def resize_disk(self, new_size):
        """resize image to given sector count"""
        if not 2 < new_size <= Disk.max_sectors:
            raise DiskError(f"Invalid disk size, expected between 2 and {Disk.max_sectors} sectors")
        if self.total_sectors % 8 != 0 or new_size % 8 != 0:
            raise DiskError("Disk size must be multiple of 8 sectors")
        old_size, self.total_sectors, self.used_sectors = self.total_sectors, new_size, 0
        self.rebuild_disk()
        self.image = (self.image[:0x0a] + chrw(new_size) +
                      self.image[0x0c:new_size * self.bytes_per_sector] +
                      self.blank_byte * ((new_size - old_size) * self.bytes_per_sector))

    def set_geometry(self, sides, density, tracks):
        """override geometry of disk image"""
        self.sides = sides or self.sides
        self.density = density or self.density
        self.sectors_per_track = Disk.default_sectors_per_track * self.density
        self.tracks_per_side = tracks or self.tracks_per_side
        self.image = (self.image[:0x0c] +
                      bytes((self.sectors_per_track,)) +
                      self.image[0x0d:0x11] +
                      bytes((self.tracks_per_side, self.sides, self.density)) +
                      self.image[0x14:])
        self.clear_warnings("geom")
        self.check_geometry()

    def fix_disk(self):
        """rebuild disk with non-erroneous files"""
        bad_files = [n for n in self.catalog if self.catalog[n].fd.error]
        for name in bad_files:
            del self.catalog[name]
        self.rebuild_disk()

    def get_tifiles_file(self, name):
        """get file in TIFiles format from disk catalog"""
        file_ = self.get_file(name)
        return file_.get_as_tifiles()

    def get_v9t9_file(self, name):
        """get file in v9t9 format from disk catalog"""
        file_ = self.get_file(name)
        return file_.get_as_v9t9()

    def get_info(self):
        """return information about disk image"""
        return "{:10s}: {:s}   {:d} used  {:d} free   {:d} KB  {:d}S/{:d}D {:d}T  {:d} S/T\n".format(
                self.name,
                "P" if self.protected else " ",
                self.used_sectors,
                self.total_sectors - self.used_sectors,
                self.total_sectors * Disk.bytes_per_sector // 1024,
                self.sides,
                self.density,
                self.tracks_per_side,
                self.sectors_per_track)

    def get_catalog(self):
        """return formatted disk catalog"""
        return "".join([self.catalog[n].fd.get_info() for n in sorted(self.catalog)])

    @staticmethod
    def blank_image(geometry, name):
        """return initialized disk image"""
        sectors, layout = Disk.parse_geometry(geometry)
        sides, density, tracks = layout or (
            2 if 360 <= (sectors - 1) % 720 else 1,
            2 if 720 < sectors <= 1440 else 1,  # favor DSSD over SSDD
            Disk.default_tracks)
        if not 2 < sectors <= Disk.max_sectors or sectors % 8 != 0 or not (sides and density):
            raise DiskError("Invalid disk size")
        sector_0 = (b"%-10b%2b%cDSK " % (name.encode()[:10],
                                         chrw(sectors),
                                         Disk.default_sectors_per_track * density) +  # header
                    bytes((tracks or Disk.default_tracks, sides, density)) +
                    bytes(0x24) +  # reserved
                    b"\x03" + bytes(sectors // 8 - 1) +  # allocation map
                    b"\xff" * (Disk.bytes_per_sector - sectors // 8 - 0x38))
        return (sector_0 +
                bytes(Disk.bytes_per_sector) +  # blank sector 1
                Disk.blank_byte * ((sectors - 2) * Disk.bytes_per_sector))  # sectors 2 and up

    @staticmethod
    def parse_geometry(geometry):
        """get disk size and layout from geometry string"""
        if geometry.upper() == "CF":
            return 1600, (1, 1, Disk.default_tracks)
        try:
            sectors = xint(geometry)
            return sectors, None
        except ValueError:
            pass
        sides, density, tracks = None, None, None
        getgeo = lambda s: 1 if s == "S" else 2 if s == "D" else int(s)
        gs = re.split(r"(\d+|[SD])([SDT])", geometry.upper())
        if "".join(gs[::3]):
            raise DiskError("Invalid disk geometry " + geometry)
        try:
            for val, part in zip(gs[1::3], gs[2::3]):
                if part == "S" and sides is None:
                    sides = getgeo(val)
                elif part == "D" and density is None:
                    density = getgeo(val)
                elif part == "T" and tracks is None:
                    tracks = getgeo(val)
                else:
                    raise DiskError("Invalid disk geometry " + geometry)
        except (IndexError, ValueError):
            raise DiskError("Invalid disk geometry " + geometry)
        try:
            sectors = sides * (tracks or Disk.default_tracks) * Disk.default_sectors_per_track * density
        except TypeError:
            sectors = None
        return sectors, (sides, density, tracks)

    def warn(self, text, category="main"):
        """issue non-critical warning"""
        if category not in self.warnings:
            self.warnings[category] = []
        if text not in self.warnings[category]:
            self.warnings[category].append(text)

    def clear_warnings(self, category):
        """clear all warnings in given category"""
        try:
            del self.warnings[category]
        except KeyError:
            pass

    def get_warnings(self):
        """return warnings issued while processing disk image"""
        return "".join([f"Warning: {w}\n"
                        for c in self.warnings.keys()
                        for w in self.warnings[c]])


# Files

class FileError(Exception):
    pass


class FileDescriptor:
    """file meta data descriptor based on TI disk image format"""

    def __init__(self, name=None, format_=None, sector=None, header=None, hostfn=None):
        self.error = False

        if sector:
            self.read_sector(sector)
        elif header:
            self.read_header(header, hostfn)
        elif name and format_:
            self.name = name
            self.create_empty(format_)
        else:
            raise RuntimeError("Incomplete file descriptor")
        self.init_disk_props(format_)

    def create_empty(self, format_):
        """create new empty file"""
        fmt_args = re.match("([PDIB])[ROGAMISNT]*(?:/?([VF])[ARIX]*\s*(\d+))?", format_.upper())
        if not fmt_args:
            raise FileError("Unknown file format: " + format_)
        fmt_type = fmt_args.group(1)
        if fmt_type == "P":
            self.flags = 0x01
            self.record_len = self.records_per_sector = 0
        else:
            fmt_fixed = fmt_args.group(2) or "V"
            fmt_len = fmt_args.group(3) or "80"
            self.flags = 0x02 if fmt_type == "I" else 0x00
            self.record_len = int(fmt_len)
            if fmt_fixed == "F":
                self.records_per_sector = (Disk.bytes_per_sector // self.record_len) % Disk.bytes_per_sector
            else:
                self.flags |= 0x80
                self.records_per_sector = (Disk.bytes_per_sector - 2) // self.record_len
        self.total_sectors = self.eof_offset = self.total_lv3_records = 0
        self.created_date, self.created_time = self.modified_date, self.modified_time = (
            self.get_date(datetime.datetime.now()))
        self.clusters = None

    def read_sector(self, sector):
        """create file based on disk image FDR sector"""
        if len(sector) < 0x20:
            raise FileError("Invalid file descriptor")
        self.name = sector[:0x0a].decode().rstrip()
        self.flags = sector[0x0c]
        self.records_per_sector = sector[0x0d]
        self.total_sectors = ordw(sector[0x0e:0x10])
        self.eof_offset = sector[0x10]
        self.record_len = sector[0x11]
        self.total_lv3_records = ordwR(sector[0x12:0x14])
        self.created_time = ordw(sector[0x14:0x16])
        self.created_date = ordw(sector[0x16:0x18])
        self.modified_time = ordw(sector[0x18:0x1a])
        self.modified_date = ordw(sector[0x1a:0x1c])
        self.clusters = sector[0x1c:]

    def read_header(self, header, hostfn):
        """create file based on TIFiles header"""
        #TODO: all 3 variants:
        if len(header) < 0x26:  # or header[:0x08] != b"\x07TIFILES":
            raise FileError("Invalid TIFiles header")
        self.total_sectors = ordw(header[0x08:0x0a])
        self.flags = header[0x0a] & 0x83
        self.records_per_sector = header[0x0b]
        self.eof_offset = header[0x0c]
        self.record_len = header[0x0d]
        self.total_lv3_records = ordwR(header[0x0e:0x10])
        if header[0x10] == 0x00:
            # short TIFiles: use file properties
            self.name = tiname(hostfn)
            dt = datetime.datetime.fromtimestamp(os.path.getctime(hostfn))
            self.created_date, self.created_time = self.get_date(dt)
            dt = datetime.datetime.fromtimestamp(os.path.getmtime(hostfn))
            self.modified_date, self.modified_time = self.get_date(dt)
        else:
            # long TIFiles: use header data
            self.name = header[0x10:0x1a].decode().rstrip()
            self.created_time = ordw(header[0x1e:0x20])
            self.created_date = ordw(header[0x20:0x22])
            self.modified_time = ordw(header[0x22:0x24])
            self.modified_date = ordw(header[0x24:0x26])
        self.clusters = None

    def init_disk_props(self, format_):
        self.format = ["DIS/", "PROGRAM", "INT/", "unknown"][self.flags & 0x03]
        self.type = format_[0] if format_ else self.format[0]
        self.fixed = self.flags & 0x80 == 0
        if self.type == "D" or self.type == "I":
            self.format += ("FI X " if self.fixed else "VAR ") + str(self.record_len)
        self.protected = self.flags & 0x08   #TODO: or "P"?
        self.created = self.read_date(self.created_date, self.created_time)
        self.modified = self.read_date(self.modified_date, self.modified_time)
        self.size = (self.total_sectors * Disk.bytes_per_sector -
                     pad(self.eof_offset, Disk.bytes_per_sector))  # excludes FDR
        self.actual_records = -1

    def read_date(self, date, time):
        """extract date and time information from header data"""
        try:
            return datetime.datetime(
                (date >> 9) + (1900 if date >> 9 >= 70 else 2000),
                date >> 5 & 0x0f, date & 0x1f, time >> 11, time >> 5 & 0x3f,
                (time & 0x0f) * 2)
        except ValueError:
            return None

    def toggle_protection(self):
        self.protected = not self.protected
        self.flags ^= 0x08

    def get_date(self, dt):
        """convert datetime object into FDR date and time word"""
        date = (dt.year % 100) << 9 | dt.month << 5 | dt.day
        time = dt.hour << 11 | dt.minute << 5 | dt.second // 2
        return date, time

    def get_sector(self):
        """return FDR as disk image sector"""
        return (b"%-10b" % self.name.encode()[:10] +
                bytes((0, 0,
                       self.flags,
                       self.records_per_sector,
                       self.total_sectors >> 8, self.total_sectors & 0xff,
                       self.eof_offset,
                       self.record_len,
                       self.total_lv3_records & 0xff, self.total_lv3_records >> 8,
                       self.created_time >> 8, self.created_time & 0xff,
                       self.created_date >> 8, self.created_date & 0xff,
                       self.modified_time >> 8, self.modified_time & 0xff,
                       self.modified_date >> 8, self.modified_date & 0xff)) +
                self.clusters)

    def get_tifiles_header(self):
        """return FDR as TIFiles header"""
        return (b"\x07TIFILES" +
                bytes((self.total_sectors >> 8, self.total_sectors & 0xff, self.flags, self.records_per_sector,
                       self.eof_offset, self.record_len, self.total_lv3_records & 0xff, self.total_lv3_records >> 8)) +
                b"%-10b" % self.name.encode()[:10] +
                bytes((0, 0, 0, 0,
                       self.created_time >> 8, self.created_time & 0xff,
                       self.created_date >> 8, self.created_date & 0xff,
                       self.modified_time >> 8, self.modified_time & 0xff,
                       self.modified_date >> 8, self.modified_date & 0xff,
                       0xff, 0xff)) +
                b" " * 88)

    def get_v9t9_header(self):
        """return FDR as v9t9 header"""
        return (b"%-10b" % self.name.encode()[:10] +
                bytes((0, 0,
                       self.flags,
                       self.records_per_sector,
                       self.total_sectors >> 8, self.total_sectors & 0xff,
                       self.eof_offset,
                       self.record_len,
                       self.total_lv3_records & 0xff, self.total_lv3_records >> 8,
                       self.created_time >> 8, self.created_time & 0xff,
                       self.created_date >> 8, self.created_date & 0xff,
                       self.modified_time >> 8, self.modified_time & 0xff,
                       self.modified_date >> 8, self.modified_date & 0xff)) +
                bytes(100))

    def get_info(self):
        """return information about file"""
        return "%-10s %4d  %-11s %6d B %8s  %c  %19s %c  %s\n" % (
            self.name,
            self.total_sectors + 1,
            self.format,
            self.size,
            "%3d recs" % self.actual_records if self.type != "P" else "",
            "P" if self.protected else " ",
            self.modified or self.created or "",
            "C" if not self.modified and self.created else " ",
            "ERR" if self.error else "")


class File:
    """main file object with FDR metadata and sector contents"""

    def __init__(self, fd=None, name=None, format_=None, tif_image=None, v9t9_image=None, data=b"", hostfn=""):
        self.warnings = []
        self.eol = os.linesep.encode()  # line termination for platform, needed for DIS files
        if fd:
            self.fd = fd
            self.data = data + bytes(pad(len(data), Disk.bytes_per_sector))
            self.read_records()
        elif tif_image:
            if not File.is_tifiles(tif_image):
                raise FileError("Invalid TIFiles image")
            self.fd = FileDescriptor(header=tif_image[:0x80], hostfn=hostfn)
            self.data = tif_image[0x80:] + bytes(pad(len(tif_image) - 0x80, Disk.bytes_per_sector))
            self.read_records()
        elif v9t9_image:
            self.fd = FileDescriptor(sector=v9t9_image[:0x80])
            self.data = v9t9_image[0x80:] + bytes(pad(len(v9t9_image) - 0x80, Disk.bytes_per_sector))
            self.read_records()
        elif name and format_:
            self.fd = FileDescriptor(name=name, format_=format_)
            self.records = self.split_contents(data)
            self.write_records()
        else:
            raise RuntimeError("Incomplete file data")

    def split_contents(self, data):
        """split blob into records"""
        if self.fd.type == "P":
            return data
        elif self.fd.fixed:
            reclen = self.fd.record_len
            return [data[i:i + reclen] for i in range(0, len(data), reclen)]
        elif self.fd.type == "D":
            return data.splitlines()
        else:
            records, p = [], 0
            while p < len(data):
                reclen = data[p] + 1
                records.append(data[p + 1:p + reclen])  # remove record length
                p += reclen
            return records

    def write_records(self):
        """create sector image from list of records (-a)"""
        if self.fd.type == "P":
            data = self.records
            self.fd.eof_offset = len(data) % Disk.bytes_per_sector
            self.fd.total_sectors = used(len(data), Disk.bytes_per_sector)
            self.fd.total_lv3_records = 0
        elif self.fd.fixed:
            data = b""
            r = s = p = 0
            for record in self.records:
                if len(record) > self.fd.record_len:
                    self.warn(f"Record #{r} too long, truncating {len(record) - self.fd.record_len} bytes")
                    record = record[:self.fd.record_len]
                if p + self.fd.record_len > Disk.bytes_per_sector:
                    data += bytes(Disk.bytes_per_sector - p)
                    s, p = s + 1, 0
                data += (record +
                         (bytes(self.fd.record_len - len(record)) if self.fd.type == "I" else
                          b" " * (self.fd.record_len - len(record))))
                r, p = r + 1, p + self.fd.record_len
            self.fd.eof_offset = p % Disk.bytes_per_sector
            self.fd.total_sectors, self.fd.total_lv3_records = s + 1, r
        else:
            data = b""
            r, s, p = 1, 0, 0
            for record in self.records:
                if len(record) > self.fd.record_len:
                    self.warn(f"Record #{r} too long, truncating {len(record) - self.fd.record_len} bytes")
                    record = record[:self.fd.record_len]
                if p + 1 + len(record) + 1 > Disk.bytes_per_sector and p > 0:
                    data += b"\xff" + bytes(Disk.bytes_per_sector - p - 1)
                    s, p = s + 1, 0
                data += bytes((len(record),)) + record
                r += 1
                if len(record) == Disk.bytes_per_sector - 1:  # VAR255
                    s, p = s + 1, 0
                else:
                    p += len(record) + 1
            if p > 0:
                data += b"\xff"  # EOF marker
                s += 1
            self.fd.eof_offset = p
            self.fd.total_sectors, self.fd.total_lv3_records = s, s
        self.data = data + bytes(pad(len(data), Disk.bytes_per_sector))

    def read_records(self):
        """extract list of records from sector image (-e)"""
        self.records = []
        if self.fd.type == "P":
            self.records = (self.data[:self.fd.eof_offset - Disk.bytes_per_sector]
                            if self.fd.eof_offset else self.data)
            self.fd.actual_records = 0
        elif self.fd.fixed:
            records_per_sector = self.fd.records_per_sector or 256
            r = rs = s = 0
            while r < self.fd.total_lv3_records:
                if rs >= records_per_sector:
                    rs, s = 0, s + 1
                    continue
                p = s * Disk.bytes_per_sector + rs * self.fd.record_len
                self.records.append(self.data[p:p + self.fd.record_len])
                r, rs = r + 1, rs + 1
            self.fd.actual_records = r
        else:
            r = rp = s = 0
            while s < self.fd.total_lv3_records:  # == self.total_sectors
                p = s * Disk.bytes_per_sector + rp
                l = self.data[p] if p < len(self.data) else -1
                if l == 0xff and rp > 0 or l == -1:
                    rp, s = 0, s + 1
                    continue
                self.records.append(self.data[p + 1:p + 1 + l])
                r += 1
                if l == 0xff and rp == 0:  # DIS/VAR255
                    s += 1
                else:
                    rp += l + 1
            self.fd.actual_records = r

    def get_contents(self, encoding=None):
        """return file contents as serialized records"""
        if self.fd.type == "P":
            return self.records
        elif self.fd.fixed:
            return b"".join(self.records)
        elif self.fd.type == "D":
            if encoding is None:
                return b"".join([r + self.eol for r in self.records])  # as binary
            else:
                try:
                    return "".join([r.encode(encoding) + "\n" for r in self.records])  # as text
                except UnicodeEncodeError:
                    raise DiskError("Bad encoding")
        else:  # "I"
            return b"".join([bytes((len(r),)) + r for r in self.records])  # add length byte

    def get_as_tifiles(self):
        """return file contents in TIFiles format"""
        return self.fd.get_tifiles_header() + self.data

    def get_as_v9t9(self):
        """return file contents in v9t9 format"""
        return self.fd.get_v9t9_header() + self.data

    @staticmethod
    def is_tifiles(image):
        """check if file image has valid TIFiles header"""
        return image[:0x08] == b"\x07TIFILES"

    def get_info(self):
        """return file meta data"""
        return self.fd.get_info()

    def warn(self, text):
        """issue non-critical warning"""
        if text not in self.warnings:
            self.warnings.append(text)

    def get_warnings(self):
        """return warnings issued while processing file"""
        return "".join(["Warning: %s\n" % w for w in self.warnings])


# Command line processing

def dump(s):
    """format binary string as hex dump"""
    result = b""
    for i in range(0, len(s), 16):
        bs, cs = b"", b""
        for j in range(16):
            try:
                bs += b"%02X " % s[i + j]
                cs += bytes((s[i + j],)) if 32 <= s[i + j] < 127 else b"."
            except IndexError:
                bs, cs = bs + b"   ", cs + b" "
            if j % 4 == 3:
                bs, cs = bs + b" ", cs + b" "
        result += b"%02X:  %b %b\n" % (i, bs, cs)
    return result


def image_cmds(opts, extdata=None):
    """disk image manipulation"""
    rc, result = 0, []
    format_ = opts.format.upper() if opts.format else "PROGRAM"
    fmt_DV = format_[0] == "D" and "F" not in format_  # DIS/VAR?

    # get disk image
    if opts.init:
        barename = os.path.splitext(os.path.basename(opts.filename))[0]
        image = Disk.blank_image(opts.init, to_ti(opts.name) or barename[:10].upper())
        result = image, opts.filename
    else:
        image = extdata or readdata(opts.filename)
    disk = Disk(image)

    # apply command to image
    if opts.print_:
        files = disk.glob_files(opts.print_)
        contents = [disk.get_file(name).get_contents() for name in files]
        sys.stdout.buffer.write(b"".join(contents))
    elif opts.extract:
        files = disk.glob_files(opts.extract)
        if opts.output and len(files) > 1 and not os.path.isdir(opts.output):
            sys.exit("Error: Supply directory with -o when extracting multiple files")
        if opts.astifiles:
            result = [(disk.get_tifiles_file(name),
                       to_pc(name).upper() if opts.tinames else to_pc(name).lower() + ".tfi")
                      for name in files]
        elif opts.asv9t9:
            result = [(disk.get_v9t9_file(name),
                       to_pc(name).upper() if opts.tinames else to_pc(name).lower() + ".v9t9")
                      for name in files]
        else:
            files = [(to_pc(name), disk.get_file(name)) for name in files]
            result = [(file_.get_contents(),
                       name.upper() if opts.tinames else name.lower())
                      for name, file_ in files]
    elif opts.add:
        seq_no = 0
        for name in opts.add:
            data = readdata(name, encoding=opts.encoding)
            if name == "-":
                name = "STDIN"
            if opts.astifiles:
                disk.add_file(File(tif_image=data, hostfn=name))
            elif opts.asv9t9:
                disk.add_file(File(v9t9_image=data))
            else:
                name = sseq(to_ti(opts.name), seq_no) if opts.name else tiname(name)
                file_, seq_no = File(name=name, format_=format_, data=data), seq_no + 1
                if file_.warnings and not opts.quiet:
                    sys.stderr.write(file_.get_warnings())
                disk.add_file(file_)
        result = (disk.image, opts.filename)
    elif opts.rename:
        names = [to_ti(arg).split(":") for arg in opts.rename]
        disk.rename_files(names)
        result = (disk.image, opts.filename)
    elif opts.delete:
        files = disk.glob_files(opts.delete)
        for name in files:
            disk.remove_file(name)
        result = (disk.image, opts.filename)
    elif opts.protect:
        files = disk.glob_files(opts.protect)
        for name in files:
            disk.protect_file(name)
        result = (disk.image, opts.filename)
    elif opts.resize:
        size, layout = Disk.parse_geometry(opts.resize)
        disk.resize_disk(size)
        if layout:
            sides, density, tracks = layout
            disk.set_geometry(sides, density, tracks or Disk.default_tracks)
        result = (disk.image, opts.filename)
    elif opts.geometry:
        size, layout = Disk.parse_geometry(opts.geometry)
        try:
            disk.set_geometry(*layout)
        except TypeError:
            raise DiskError("Invalid disk geometry " + opts.geometry)
        result = (disk.image, opts.filename)
    elif opts.checkonly:
        rc = 1 if disk.warnings else 0
    elif opts.repair:
        disk.fix_disk()
        result = (disk.image, opts.filename)
    elif opts.sector:
        opts.quiet = True
        try:
            sno = xint(opts.sector)
            sector = disk.get_sector(sno)
        except (IndexError, ValueError):
            raise DiskError(f"Invalid sector {opts.sector}")
        result = (dump(sector), "-")  #TODO: list?
    elif opts.name and not opts.init:
        # at this point, "-n" is supplied without command, so rename disk
        disk.rename(to_ti(opts.name))
        result = (disk.image, opts.filename)
    elif opts.info or not opts.init:
        sys.stdout.write(disk.get_info())
        sys.stdout.write("-" * 76 + "\n")
        sys.stdout.write(disk.get_catalog())
    if not opts.quiet:
        sys.stderr.write(disk.get_warnings())

    return rc, result


def file_cmds(opts):
    """file manipulation"""
    rc, result = 0, []

    # files in a directory
    files = opts.fromfiad or opts.tofiad or opts.printfiad or opts.infofiad
    if opts.output and len(files) > 1:
        sys.exit("Error: Cannot use -o when converting multiple files")
    fmt = opts.format.upper() if opts.format else "PROGRAM"
    for fi, fn in enumerate(files):
        image = readdata(fn)
        if opts.tofiad:
            n = sseq(to_ti(opts.name), fi) if opts.name else tiname(fn)
            f = File(name=n, format_=fmt, data=image)
            if opts.asv9t9:
                result.append((f.get_as_v9t9(), fn + ".v9t9"))
            else:
                result.append((f.get_as_tifiles(), fn + ".tfi"))
        else:
            is_tifiles = opts.astifiles or (not opts.asv9t9 and File.is_tifiles(image))
            f = File(tif_image=image, hostfn=fn) if is_tifiles else File(v9t9_image=image)
            if opts.fromfiad:
                result.append((f.get_contents(), os.path.splitext(fn)[0]))
            elif opts.printfiad:
                result.append((f.get_contents(), "-"))
            else:
                sys.stdout.write(f.get_info())

    return rc, result


def main(argv, extdata=None):
    import os
    import argparse
    import glob

    class GlobStore(argparse.Action):
        """argparse globbing for Windows platforms"""

        def __call__(self, parser, namespace, values, option_string=None):
            if os.name == "nt":
                names = [glob.glob(fn) if "*" in fn or "?" in fn else [fn]
                         for fn in values]
                values = [f for n in names for f in n]
            setattr(namespace, self.dest, values)

    args = argparse.ArgumentParser(
        description="xdm99: Disk image and file manipulation tool, v" + VERSION)
    args.add_argument(
        "filename", nargs="?", type=str,
        help="disk image filename")
    cmd = args.add_mutually_exclusive_group()
    # used argument identifiers: adefhinopqrtu CFIPRSTXZ 9

    # disk image commands
    cmd.add_argument(
        "-i", "--info", action="store_true", dest="info",
        help="show image infomation")
    cmd.add_argument(
        "-p", "--print", dest="print_", nargs="+", metavar="<name>",
        help="print file from image")
    cmd.add_argument(
        "-e", "--extract", dest="extract", nargs="+", metavar="<name>",
        help="extract files from image")
    cmd.add_argument(
        "-a", "--add", action=GlobStore, dest="add", nargs="+",
        metavar="<file>", help="add files to image or update existing files")
    cmd.add_argument(
        "-r", "--rename", dest="rename", nargs="+", metavar="<old>:<new>",
        help="rename files on image")
    cmd.add_argument(
        "-d", "--delete", dest="delete", nargs="+", metavar="<name>",
        help="delete files from image")
    cmd.add_argument(
        "-w", "--protect", dest="protect", nargs="+", metavar="<name>",
        help="toggle write protection of files on image")
    cmd.add_argument(
        "-c", "--encoding", dest="encoding", nargs="?", const="utf-8", metavar="<encoding>",
        help="set encoding for DISPLAY files")
    cmd.add_argument(
        "-Z", "--resize", dest="resize", metavar="<sectors>",
        help="resize image to given total sector count")
    cmd.add_argument(
        "--set-geometry", dest="geometry", metavar="<geometry>",
        help="set disk geometry (xSxDxT)")
    cmd.add_argument(
        "-C", "--check", action="store_true", dest="checkonly",
        help="check disk image integrity only")
    cmd.add_argument(
        "-R", "--repair", action="store_true", dest="repair",
        help="attempt to repair disk image")
    cmd.add_argument(
        "-S", "--sector", dest="sector", metavar="<sector>",
        help="dump disk sector")

    # FIAD commands
    cmd.add_argument(
        "-P", "--print-fiad", action=GlobStore, dest="printfiad", nargs="+",
        metavar="<file>", help="print contents of file in FIAD format")
    cmd.add_argument(
        "-T", "--to-fiad", action=GlobStore, dest="tofiad", nargs="+",
        metavar="<file>", help="convert plain file to FIAD format")
    cmd.add_argument(
        "-F", "--from-fiad", action=GlobStore, dest="fromfiad", nargs="+",
        metavar="<file>", help="convert FIAD format to plain file")
    cmd.add_argument(
        "-I", "--info-fiad", action=GlobStore, dest="infofiad", nargs="+",
        metavar="<file>", help="show information about file in FIAD format")

    # general options
    args.add_argument(
        "-t", "--tifiles", action="store_true", dest="astifiles",
        help="use TIFiles file format for added/extracted files")
    args.add_argument(
        "--ti-names", action="store_true", dest="tinames",
        help="use TI filenames for extracted files")
    args.add_argument(
        "-9", "--v9t9", action="store_true", dest="asv9t9",
        help="use v9t9 file format for added/extracted files")
    args.add_argument(
        "-f", "--format", dest="format", metavar="<format>",
        help="set TI file format (DIS/VARxx, DIS/FIXxx, INT/VARxx, " + \
             "INT/FIXxx, PROGRAM) for data to add")
    args.add_argument(
        "-n", "--name", dest="name", metavar="<name>",
        help="set TI filename for data to add")
    args.add_argument(
        "-X", "--initialize", dest="init", metavar="<size>",
        help="initialize disk image (sector count or disk geometry xSxDxT)")
    args.add_argument(
        "-o", "--output", dest="output", metavar="<file>",
        help="set output filename")
    args.add_argument(
        "-q", "--quiet", action="store_true", dest="quiet",
        help="suppress all warnings")
    opts = args.parse_args(argv)

    # process image
    try:
        if opts.fromfiad or opts.tofiad or opts.printfiad or opts.infofiad:
            rc, result = file_cmds(opts)
        elif not opts.filename:
            args.print_usage(sys.stderr)
            sys.exit("Error: Missing disk image")
        else:
            rc, result = image_cmds(opts, extdata)
    except (IOError, DiskError, FileError) as e:
        sys.exit("Error: " + str(e))

    # process result
    if extdata:
        return result

    # write result
    if opts.output and os.path.isdir(opts.output):  # -o file or directory?
        path, opts.output = opts.output, None
    else:
        path = ""
    if isinstance(result, tuple):  # main file manipulation
        result = [result]
    for data, name in result:
        outname = os.path.join(path, opts.output or name)
        try:
            writedata(outname, data, encoding=opts.encoding)
        except IOError as e:
            sys.exit(f"Error: {e}")

    # return status
    return rc


if __name__ == "__main__":
    status = main(sys.argv[1:])
    sys.exit(status)
