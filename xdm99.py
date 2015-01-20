#!/usr/bin/env python

# xdm99: A disk manager for TI disk images
#
# Copyright (c) 2015 Ralph Benzinger <xdt99@endlos.net>
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

VERSION = "1.2.0"


### Utility functions

def ordw(word):
    """word ord"""
    return ord(word[0]) << 8 | ord(word[1])


def ordwR(word):
    """reverse word ord"""
    return ord(word[1]) << 8 | ord(word[0])


def chrw(word):
    """word chr"""
    return chr(word >> 8) + chr(word & 0xFF)


def pad(n, m):
    """return increment to next multiple of m"""
    return -n % m


def used(n, m):
    """integer devision rounding up"""
    return (n + m - 1) / m


### Sector-based disk image

class DiskError(Exception):
    pass


class Disk:
    """sector-based TI disk image file"""

    bytesPerSector = 256
    maxSectors = 1600

    def __init__(self, image):
        if len(image) < 2 * Disk.bytesPerSector:
            raise DiskError("Invalid disk image")
        self.image = image
        self.readSectors = []
        self.warnings = []
        # meta data
        sector0 = self.getSector(0)
        self.name = sector0[:0x0A]
        self.totalSectors = ordw(sector0[0x0A:0x0C])
        self.sectorsPerTrack = ord(sector0[0x0C])
        self.dsk = sector0[0x0D:0x10]
        self.protected = ord(sector0[0x10])
        self.tracksPerSide = ord(sector0[0x11])
        self.sides = ord(sector0[0x12])
        self.density = ord(sector0[0x13])
        self.allocBitmap = sector0[0x38:]
        # derived values and sanity checks
        if self.dsk != "DSK":
            raise DiskError("Disk image not initialized")
        if len(self.image) < self.totalSectors * Disk.bytesPerSector:
            self.warn("Disk image truncated")
        if (self.totalSectors !=
                self.sides * self.tracksPerSide * self.sectorsPerTrack) or (
                self.totalSectors % 8 != 0):
            self.warn("Unusual total sector count: %d" % self.totalSectors)
        self.usedSectors = 0
        try:
            for i in xrange(used(self.totalSectors, 8)):
                self.usedSectors += bin(ord(self.allocBitmap[i])).count("1")
        except IndexError:
            self.warn("Allocation map corrupted")
        self.catalog = {}
        self.initCatalog()
        self.checkAllocation()

    def initCatalog(self):
        """read all files from disk"""
        sector1 = self.getSector(1)
        scount = 0
        for i in xrange(0, Disk.bytesPerSector, 2):
            # get file descriptor
            fdIndex = ordw(sector1[i:i + 2])
            if fdIndex == 0:
                break
            try:
                fdSector = self.getSector(fdIndex, "FDR#" + str(fdIndex))
            except IndexError:
                self.warn("File descriptor index corrupted")
                continue
            fd = FileDescriptor(sector=fdSector)
            # get file contents
            data, error = self.readFile(fd.name, fd.totalSectors, fd.clusters)
            if error:
                fd.error = True
            self.catalog[fd.name] = File(fd=fd, data=data)
            scount += fd.totalSectors + 1
        # consistency check
        if scount != self.usedSectors - 2:
            self.warn(
                "Used sector mismatch: found %d file sectors, expected %d" % (
                    scount, self.usedSectors - 2))

    def readFile(self, name, sectors, clusters):
        """read file contents based on FDR cluster data"""
        data, error = "", False
        offset = -1
        for p in xrange(0, len(clusters) - 2, 3):
            start = ord(clusters[p]) | (ord(clusters[p + 1]) & 0x0F) << 8
            if start == 0:
                break
            prev, offset = offset, ord(clusters[p + 1]) >> 4 | ord(
                clusters[p + 2]) << 4
            for i in xrange(offset - prev):
                try:
                    data += self.getSector(start + i, name)
                except IndexError:
                    self.warn("%s: File contents corrupted" % name)
                    error = True
                    continue
        if len(data) != sectors * Disk.bytesPerSector:
            self.warn("%s: File size mismatch: found %d bytes, expected %d" % (
                name, len(data), sectors * Disk.bytesPerSector))
            error = True
        return data, error

    def rebuildDisk(self):
        """rebuild disk metadata after changes to file catalog"""
        requiredSectors = sum([self.catalog[n].fd.totalSectors
                               for n in self.catalog])
        # preferred start at sector >22
        firstFree = nextFree = min(max(2 + len(self.catalog), 0x22),
                                   self.totalSectors - requiredSectors)
        if firstFree < 2 + len(self.catalog):
            raise DiskError("Disk full, lacking %d sectors" % (
                2 + len(self.catalog) - firstFree))
        index, sector1 = 2, ""
        for n in sorted(self.catalog):
            f = self.catalog[n]
            # put file data into single cluster
            data = f.getData()
            for j in range(f.fd.totalSectors):
                self.setSector(nextFree + j,
                               data[Disk.bytesPerSector * j:
                                    Disk.bytesPerSector * (j + 1)])
            # build file descriptor
            start, offset = (
                (nextFree, f.fd.totalSectors - 1) if f.fd.totalSectors > 0 else
                (0, 0))
            f.fd.clusters = "%c%c%c" % (
                start & 0xFF, start >> 8 | (offset & 0xF) << 4, offset >> 4
                ) + "\x00" * (Disk.bytesPerSector - 0x1C - 3)
            self.setSector(index, f.fd.getSector())
            # update FDR index in sector 1
            sector1 += chrw(index)
            index, nextFree = index + 1, nextFree + f.fd.totalSectors
        sector1 += "\x00" * (Disk.bytesPerSector - len(sector1))
        self.setSector(1, sector1)
        # update allocation bitmap in sector 0 (used: 0..i-1, ff..nf-1)
        assert 0 < index <= firstFree <= nextFree
        mask = int("1" * (nextFree - firstFree) +
                   "0" * (firstFree - index) + "1" * index, 2)
        bitmap = ""
        for i in xrange(self.totalSectors / 8):
            bitmap += chr(mask & 0xFF)
            mask >>= 8
        bitmap += "\xFF" * (Disk.bytesPerSector - 0x38 - len(bitmap))
        self.allocBitmap = bitmap
        sector0 = self.getSector(0)
        self.setSector(0, sector0[:0x38] + bitmap)

    @staticmethod
    def extendSectors(image, newsize):
        """increase total number of sectors and clear alloc map (for xvm99)"""
        current = ordw(image[0x0A:0x0C])
        if not current <= newsize <= Disk.maxSectors:
            raise DiskError("Invalid size %d for sector increase" % newsize)
        if current % 8 != 0:
            raise DiskError("Unsupported total sector count of %d" % current)
        bitmap = (image[0x38:0x38 + current / 8] +
                  "\xFF" * (Disk.bytesPerSector - 0x38 - current / 8))
        return (image[:0x0A] + chrw(newsize) + image[0x0C:0x38] +
                bitmap + image[0x100:])

    @staticmethod
    def trimSectors(image):
        """shrink image to actually existing sectors"""
        totalSectors = ordw(image[0x0A:0x0C])
        return image[:totalSectors * Disk.bytesPerSector]

    def getSector(self, n, context=None):
        """retrieve sector from image"""
        if n > 0 and n > self.totalSectors:
            raise IndexError("Invalid sector number")
        if context:
            self.readSectors.append((n, context))
        offset = n * Disk.bytesPerSector
        return self.image[offset:offset + Disk.bytesPerSector]

    def setSector(self, n, data):
        """write sector to image"""
        if n > self.totalSectors:
            raise IndexError("Invalid sector number")
        if len(data) != Disk.bytesPerSector:
            raise ValueError(
                "Invalid data for sector %d: found %d bytes, expected %d" % (
                    n, len(data), Disk.bytesPerSector))
        offset = n * Disk.bytesPerSector
        self.image = (self.image[:offset] + data +
                      self.image[offset + Disk.bytesPerSector:])

    def getFile(self, name):
        """get File object from disk catalog"""
        if name not in self.catalog:
            raise DiskError("File %s not found" % name)
        return self.catalog[name]

    def addFile(self, file_):
        """add or update File object in image"""
        self.catalog[file_.fd.name] = file_
        self.rebuildDisk()

    def removeFile(self, name):
        """remove file from image"""
        if name not in self.catalog:
            raise DiskError("File %s not found" % name)
        del self.catalog[name]
        self.rebuildDisk()

    def renameFiles(self, names):
        """rename files in image"""
        for (old, new) in names:
            if old not in self.catalog:
                raise DiskError("File %s not found" % old)
            if new in self.catalog:
                raise DiskError("File %s already exists" % new)
            self.catalog[old].fd.name = new
            self.catalog[new] = self.catalog[old]
            del self.catalog[old]
        self.rebuildDisk()

    def checkAllocation(self):
        """check sector allocation for consistency"""
        reads = {n: [] for n in xrange(self.totalSectors)}
        allocated = []
        for i in xrange(used(self.totalSectors, 8)):
            byte = ord(self.allocBitmap[i])
            for j in xrange(8):
                allocated.append(byte & 1 << j != 0)
        # unallocated sectors
        for n, context in self.readSectors:
            reads[n].append(context)
            if context and not allocated[n]:
                self.warn("%s: Used sector %d not allocated" % (context, n))
                f = self.catalog.get(context)
                if f:
                    f.fd.error = True
        # sectors allocated to multiple files
        for n, files in [(i, reads[i]) for i in reads if len(reads[i]) > 1]:
            self.warn("%s: Sector %d claimed by multiple files" % (
                "/".join(files), n))
            for name in files:
                f = self.catalog.get(name)
                if f:
                    f.fd.error = True

    def resizeDisk(self, newsize):
        """resize image to given sector count"""
        self.usedSectors = 0
        if not self.usedSectors <= newsize <= Disk.maxSectors:
            raise DiskError(
                "Invalid disk size %d, expected between %d and %d sectors" % (
                    self.usedSectors, newsize, Disk.maxSectors))
        if self.totalSectors % 8 != 0 or newsize % 8 != 0:
            raise DiskError("Disk size must be multiple of 8 sectors")
        oldsize, self.totalSectors = self.totalSectors, newsize
        self.rebuildDisk()
        self.image = (self.image[:0x0A] + chrw(newsize) +
                      self.image[0x0C:newsize * self.bytesPerSector] +
                      "\x00" * ((newsize - oldsize) * self.bytesPerSector))

    def fixDisk(self):
        """rebuild disk with non-erroneous files"""
        badFiles = [n for n in self.catalog if self.catalog[n].fd.error]
        for name in badFiles:
            del self.catalog[name]
        self.rebuildDisk()

    def getImage(self):
        """return disk image"""
        return self.image

    def getTifile(self, name):
        """get file in TIFile format from disk catalog"""
        f = self.getFile(name)
        return f.getAsTifile()

    def getInfo(self):
        """return information about disk image"""
        return "%10s: %c   %d used  %d free   %d KB  %dS/%dD  %2d TpS\n" % (
            self.name, self.protected,
            self.usedSectors, self.totalSectors - self.usedSectors,
            self.totalSectors * Disk.bytesPerSector / 1024,
            self.sides, self.density, self.tracksPerSide)

    def getCatalog(self):
        """return formatted disk catalog"""
        return "".join([self.catalog[n].fd.getInfo()
                        for n in sorted(self.catalog)])

    def warn(self, text):
        """issue non-critical warning"""
        if text not in self.warnings:
            self.warnings.append(text)

    def getWarnings(self):
        """return warnings issued while processing disk image"""
        return "".join(["Warning: %s\n" % w for w in self.warnings])


### Files

class FileError(Exception):
    pass


class FileDescriptor:
    """file meta data descriptor based on TI disk image format"""

    def __init__(self, name=None, fmt=None, sector=None, header=None):
        if sector:
            self.initSector(sector)
        elif header:
            self.initHeader(header)
        elif name and fmt:
            self.init(name, fmt)
        else:
            raise RuntimeError("Incomplete file descriptor")
        self.format = ["DIS/", "PROGRAM", "INT/", "unknown"][self.flags & 0x03]
        self.type = self.format[0]
        self.fixed = self.flags & 0x80 == 0
        if self.type == "D" or self.type == "I":
            self.format += (("FIX " if self.fixed else "VAR ") +
                            str(self.recordLen))
        self.protected = self.flags & 0x08 != 0x00
        self.created = self.initDate(self.createdDate, self.createdTime)
        self.modified = self.initDate(self.modifiedDate, self.modifiedTime)
        self.size = (self.totalSectors * Disk.bytesPerSector -
                     pad(self.eofOffset, Disk.bytesPerSector))  # excludes FDR
        self.actualRecords = -1
        self.error = False

    def init(self, name, fmt):
        """create new empty file"""
        fmtargs = re.match("([PDI])[ROGRAMISNT]*(?:/?([VF])[ARIX]*\s*(\d+))?",
                           fmt.upper())
        if not fmtargs:
            raise FileError("Unknown file format: " + fmt)
        fmttype = fmtargs.group(1)
        self.name = name
        if fmttype == "P":
            self.flags = 0x01
            self.recordLen = self.recordsPerSector = 0
        else:
            fmtfixed = fmtargs.group(2) or "V"
            fmtlen = fmtargs.group(3) or "80"
            self.flags = 0x02 if fmttype == "I" else 0x00
            self.recordLen = int(fmtlen)
            if fmtfixed == "F":
                self.recordsPerSector = (Disk.bytesPerSector /
                                         self.recordLen) % Disk.bytesPerSector
            else:
                self.flags |= 0x80
                self.recordsPerSector = ((Disk.bytesPerSector - 2) /
                                         self.recordLen)
        self.totalSectors = self.eofOffset = self.totalLv3Records = 0
        now = datetime.datetime.now()
        self.createdDate = self.modifiedDate = (
            (now.year % 100) << 9 | now.month << 5 | now.day)
        self.createdTime = self.modifiedTime = (
            now.hour << 11 | now.minute << 5 | now.second / 2)
        self.clusters = None

    def initSector(self, sector):
        """create file based on disk image FDR sector"""
        if len(sector) < 0x20:
            raise FileError("Invalid file descriptor")
        self.name = sector[:0x0A].rstrip()
        self.flags = ord(sector[0x0C])
        self.recordsPerSector = ord(sector[0x0D])
        self.totalSectors = ordw(sector[0x0E:0x10])
        self.eofOffset = ord(sector[0x10])
        self.recordLen = ord(sector[0x11])
        self.totalLv3Records = ordwR(sector[0x12:0x14])
        self.createdTime = ordw(sector[0x14:0x16])
        self.createdDate = ordw(sector[0x16:0x18])
        self.modifiedTime = ordw(sector[0x18:0x1A])
        self.modifiedDate = ordw(sector[0x1A:0x1C])
        self.clusters = sector[0x1C:]

    def initHeader(self, header):
        """create file based on TIFile header"""
        if len(header) < 0x26 or header[:0x08] != "\x07TIFILES":
            raise FileError("Invalid TIFile header")
        self.name = header[0x10:0x1A].rstrip()
        self.flags = ord(header[0x0A]) & 0x81
        self.recordsPerSector = ord(header[0x0B])
        self.totalSectors = ordw(header[0x08:0x0A])
        self.eofOffset = ord(header[0x0C])
        self.recordLen = ord(header[0x0D])
        self.totalLv3Records = ordwR(header[0x0E:0x10])
        self.createdTime = ordw(header[0x1E:0x20])
        self.createdDate = ordw(header[0x20:0x22])
        self.modifiedTime = ordw(header[0x22:0x24])
        self.modifiedDate = ordw(header[0x24:0x26])
        self.clusters = None

    def initDate(self, date, time):
        """extract date and time information from header data"""
        try:
            return datetime.datetime(
                (date >> 9) + (1900 if date >> 9 >= 70 else 2000),
                date >> 5 & 0x0F, date & 0x1F, time >> 11, time >> 5 & 0x3F,
                (time & 0x0F) * 2)
        except ValueError:
            return None

    def getSector(self):
        """return FDR as disk image sector"""
        return "%-10s\x00\x00%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c" % (
            self.name[:10], self.flags, self.recordsPerSector,
            self.totalSectors >> 8, self.totalSectors & 0xFF,
            self.eofOffset, self.recordLen,
            self.totalLv3Records & 0xFF, self.totalLv3Records >> 8,
            self.createdTime >> 8, self.createdTime & 0xFF,
            self.createdDate >> 8, self.createdDate & 0xFF,
            self.modifiedTime >> 8, self.modifiedTime & 0xFF,
            self.modifiedDate >> 8, self.modifiedDate & 0xFF,
        ) + self.clusters

    def getTifileHeader(self):
        """return FDR as TIFile header"""
        return "\x07TIFILES%c%c%c%c%c%c%c%c%-10s\x00\x00\x00\x00%c%c%c%c%c%c%c%c\xFF\xFF" % (
            self.totalSectors >> 8, self.totalSectors & 0xFF,
            self.flags, self.recordsPerSector, self.eofOffset, self.recordLen,
            self.totalLv3Records & 0xFF, self.totalLv3Records >> 8,
            self.name[:10],
            self.createdTime >> 8, self.createdTime & 0xFF,
            self.createdDate >> 8, self.createdDate & 0xFF,
            self.modifiedTime >> 8, self.modifiedTime & 0xFF,
            self.modifiedDate >> 8, self.modifiedDate & 0xFF
        ) + " " * 88

    def getInfo(self):
        """return information about file"""
        return "%-10s  %4d  %-11s %6d B  %8s  %19s %c  %s\n" % (
            self.name, self.totalSectors + 1, self.format, self.size,
            "%3d recs" % self.actualRecords if self.type != "P" else "",
            self.modified or self.created or "",
            "C" if not self.modified and self.created else " ",
            "ERR" if self.error else "")


class File:
    """main file object with FDR metadata and sector contents"""

    def __init__(self, fd=None, name=None, fmt=None, tifimage=None, data=""):
        if fd:
            self.fd = fd
            self.data = data + "\x00" * pad(len(data), Disk.bytesPerSector)
            self.readRecords()
        elif tifimage:
            if not File.isTifile(tifimage):
                raise FileError("Invalid TIFile image")
            self.fd = FileDescriptor(header=tifimage[:0x80])
            self.data = (tifimage[0x80:] + "\x00" * pad(len(tifimage) - 0x80,
                                                        Disk.bytesPerSector))
            self.readRecords()
        elif name and fmt:
            self.fd = FileDescriptor(name=name, fmt=fmt)
            self.records = self.splitRecords(data)
            self.writeRecords()
        else:
            raise RuntimeError("Incomplete file data")

    def splitRecords(self, data):
        """split blob into records"""
        if self.fd.type == "P":
            return data
        elif self.fd.type == "D":
            return data.splitlines()
        elif self.fd.fixed:
            l = self.fd.recordLen  # keep length byte
            return [data[i:i + l] for i in xrange(0, len(data), l)]
        else:
            records, p = [], 0
            while p < len(data):
                l = ord(data[p]) + 1
                records.append(data[p:p + l])
                p += l
            return records

    def writeRecords(self):
        """create sector image from list of records"""
        if self.fd.type == "P":
            data = self.records
            self.fd.eofOffset = len(data) % Disk.bytesPerSector
            self.fd.totalSectors = used(len(data), Disk.bytesPerSector)
            self.fd.totalLv3Records = 0
        elif self.fd.fixed:
            data = ""
            r, s, p = 0, 0, 0
            for record in self.records:
                if len(record) > self.fd.recordLen:
                    raise FileError(
                        "Record #%d too long: found %d bytes, exceeds %d" % (
                            r + 1, len(record), self.fd.recordLen))
                if p + self.fd.recordLen > Disk.bytesPerSector:
                    data += "\x00" * (Disk.bytesPerSector - p)
                    s, p = s + 1, 0
                data += record + (" " if self.fd.type == "D" else "\x00") * (
                    self.fd.recordLen - len(record))
                r, p = r + 1, p + self.fd.recordLen
            self.fd.eofOffset = p % Disk.bytesPerSector
            self.fd.totalSectors, self.fd.totalLv3Records = s + 1, r
        else:
            data = ""
            r, s, p = 1, 0, 0
            for record in self.records:
                if len(record) > self.fd.recordLen:
                    raise FileError("Record #%d too long: %d" % (
                        r, len(record)))
                if p + 1 + len(record) + 1 > Disk.bytesPerSector and p > 0:
                    data += "\xFF" + "\x00" * (Disk.bytesPerSector - p - 1)
                    s, p = s + 1, 0
                data += chr(len(record)) + record
                r += 1
                if len(record) == Disk.bytesPerSector - 1:  # VAR255
                    s, p = s + 1, 0
                else:
                    p += len(record) + 1
            if p > 0:
                data += "\xFF"  # EOF marker
                s += 1
            self.fd.eofOffset = p
            self.fd.totalSectors, self.fd.totalLv3Records = s, s
        self.data = data + "\x00" * pad(len(data), Disk.bytesPerSector)

    def readRecords(self):
        """extract list of records from sector image"""
        self.records = []
        if self.fd.type == "P":
            self.records = (self.data[:self.fd.eofOffset -
                                       Disk.bytesPerSector]
                            if self.fd.eofOffset else self.data)
            self.fd.actualRecords = 0
        elif self.fd.fixed:
            recordsPerSector = self.fd.recordsPerSector or 256
            r, rs, s = 0, 0, 0
            while r < self.fd.totalLv3Records:
                if rs >= recordsPerSector:
                    rs, s = 0, s + 1
                    continue
                p = s * Disk.bytesPerSector + rs * self.fd.recordLen
                self.records.append(self.data[p:p + self.fd.recordLen])
                r, rs = r + 1, rs + 1
            self.fd.actualRecords = r
        else:
            r, rp, s = 0, 0, 0
            while s < self.fd.totalLv3Records:  # == self.totalSectors
                p = s * Disk.bytesPerSector + rp
                l = ord(self.data[p]) if p < len(self.data) else -1
                if l == 0xFF and rp > 0 or l == -1:
                    rp, s = 0, s + 1
                    continue
                self.records.append(self.data[p + 1:p + 1 + l])
                r += 1
                if l == 0xFF and rp == 0:  # DIS/VAR255
                    s += 1
                else:
                    rp += l + 1
            self.fd.actualRecords = r

    def getData(self):
        """return file contents as raw sector data"""
        return self.data

    def getContents(self):
        """return file contents as serialized records"""
        if self.fd.type == "P":
            return self.records
        elif self.fd.type == "D":
            return "".join([r + "\n" for r in self.records])
        else:
            return "".join(self.records)  # keep length byte

    def getAsTifile(self):
        """return file contents in TIFile format"""
        return self.fd.getTifileHeader() + self.getData()

    def getInfo(self):
        """return file meta data"""
        return self.fd.getInfo()

    @staticmethod
    def isTifile(image):
        """check if file image has valid TIFile header"""
        return image[:0x08] == "\x07TIFILES"


### Command line processing

def dump(s):
    """format binary string as hex dump"""
    result = ""
    for i in range(0, len(s), 16):
        bs, cs = "", ""
        for j in range(16):
            try:
                bs += "%02X " % ord(s[i + j])
                cs += s[i + j] if 32 <= ord(s[i + j]) < 127 else "."
            except IndexError:
                bs, cs = bs + "   ", cs + " "
            if j % 4 == 3:
                bs, cs = bs + " ", cs + " "
        result += "%02X:  %s %s\n" % (i, bs, cs)
    return result


def main():
    import argparse, os.path

    args = argparse.ArgumentParser(
        version=VERSION,
        description="xdm99: Disk image and file manipulation tool")
    args.add_argument(
        "filename", type=str,
        help="disk image or file name")
    cmd = args.add_mutually_exclusive_group()
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
    args.add_argument(
        "-t", "--tifile", action="store_true", dest="astif",
        help="use TIFile file format for extracted files")
    cmd.add_argument(
        "-a", "--add", dest="add", nargs="+", metavar="<file>",
        help="add files to image or update existing files")
    args.add_argument(
        "-f", "--format", dest="format", metavar="<format>",
        help="set TI file format (DIS/VARnnn, DIS/FIXnnn, INT/VARnnn, " + \
             "INT/FIXnnn, PROGRAM) for data to add")
    args.add_argument(
        "-n", "--name", dest="name", metavar="<name>",
        help="set TI file name for data to add")
    cmd.add_argument(
        "-r", "--rename", dest="rename", nargs="+", metavar="<old>:<new>",
        help="rename files on image")
    cmd.add_argument(
        "-d", "--delete", dest="delete", nargs="+", metavar="<name>",
        help="delete files from image")
    cmd.add_argument(
        "-Z", "--resize", dest="resize", metavar="<sectors>",
        help="resize image to given total sector count")
    cmd.add_argument(
        "-c", "--check", action="store_true", dest="checkonly",
        help="check disk image integrity only")
    cmd.add_argument(
        "-R", "--repair", action="store_true", dest="repair",
        help="attempt to repair disk image")
    cmd.add_argument(
        "-s", "--sector", dest="sector", metavar="<sector>",
        help="dump disk sector")
    # TIFile commands
    args.add_argument(
        "-P", "--print-tifile", action="store_true", dest="printtif",
        help="print contents of file in TIFile format")
    args.add_argument(
        "-T", "--to-tifile", action="store_true", dest="totif",
        help="convert plain file to TIFile format")
    args.add_argument(
        "-F", "--from-tifile", action="store_true", dest="fromtif",
        help="convert TIFile format to plain file")
    args.add_argument(
        "-I", "--info-tifile", action="store_true", dest="infotif",
        help="show TIFile file information")
    # general options
    args.add_argument(
        "-o", "--output", dest="output", metavar="<file>",
        help="set output file name")
    args.add_argument(
        "-q", "--quiet", action="store_true", dest="quiet",
        help="suppress all warnings")
    opts = args.parse_args()

    # setup
    try:
        with open(opts.filename, "rb") as fin:
            image = fin.read()
    except IOError as e:
        sys.exit("Error: " + str(e))
    fmt = opts.format or "PROGRAM"
    tiname = lambda x: (opts.name or
                        os.path.splitext(os.path.basename(x))[0][:10].upper())

    # process image
    rc, result = 0, []
    try:
        # TIFile
        if opts.fromtif:
            tifile = File(tifimage=image)
            result = [(tifile.getContents(),
                       os.path.splitext(opts.filename)[0],
                       "w" if tifile.fd.type == "D" else "wb")]
        elif opts.totif:
            tifile = File(name=tiname(opts.filename), fmt=fmt, data=image)
            result = [(tifile.getAsTifile(), opts.filename + ".tfi", "wb")]
        elif opts.printtif:
            tifile = File(tifimage=image)
            result = [(tifile.getContents(), "-", "w")]
        elif opts.infotif or File.isTifile(image):
            tifile = File(tifimage=image)
            sys.stdout.write(tifile.getInfo())
        # disk image
        else:
            disk = Disk(image)
            if opts.print_:
                contents = [disk.getFile(name).getContents()
                            for name in opts.print_]
                sys.stdout.write("".join(contents))
            elif opts.extract:
                if opts.output and len(opts.extract) > 1:
                    sys.exit(
                        "Error: Cannot use -o when extracting multiple files")
                if opts.astif:
                    result = [(disk.getTifile(name),
                               name.lower() + ".tfi", "wb")
                              for name in opts.extract]
                else:
                    result = [(disk.getFile(name).getContents(),
                               name.lower(), "w" if fmt[0] == "D" else "wb")
                              for name in opts.extract]
            elif opts.add:
                if opts.name and len(opts.add) > 1:
                    sys.exit(
                        "Error: Cannot use -n when adding multiple files")
                for name in opts.add:
                    try:
                        if name == "-":
                            name = "STDIN"
                            data = sys.stdin.read()
                        else:
                            with open(name, "r" if fmt[0] == "D" and
                                            not opts.astif else "rb") as fin:
                                data = fin.read()
                    except IOError as e:
                        sys.exit("Error: " + str(e))
                    f = (File(tifimage=data) if opts.astif else
                         File(name=tiname(name), fmt=fmt, data=data))
                    disk.addFile(f)
                result = [(disk.getImage(), opts.filename, "wb")]
            elif opts.rename:
                names = [arg.split(":") for arg in opts.rename]
                disk.renameFiles(names)
                result = [(disk.getImage(), opts.filename, "wb")]
            elif opts.delete:
                for name in opts.delete:
                    disk.removeFile(name)
                result = [(disk.getImage(), opts.filename, "wb")]
            elif opts.resize:
                try:
                    size = int(opts.resize,
                               16 if opts.resize[:2] == "0x" else 10)
                except ValueError:
                    raise DiskError("Invalid disk size %s" % opts.resize)
                disk.resizeDisk(size)
                result = [(disk.getImage(), opts.filename, "wb")]
            elif opts.checkonly:
                rc = 1 if disk.warnings else 0
            elif opts.repair:
                disk.fixDisk()
                result = [(disk.getImage(), opts.filename, "wb")]
            elif opts.sector:
                opts.quiet = True
                try:
                    sno = int(opts.sector,
                              16 if opts.sector[:2] == "0x" else 10)
                    sector = disk.getSector(sno)
                except (IndexError, ValueError):
                    raise DiskError("Invalid sector %s" % opts.sector)
                result = [(dump(sector), "-", "w")]
            else:
                sys.stdout.write(disk.getInfo())
                sys.stdout.write("-" * 76 + "\n")
                sys.stdout.write(disk.getCatalog())
            if not opts.quiet:
                sys.stderr.write(disk.getWarnings())
    except (DiskError, FileError) as e:
        sys.exit("Error: " + str(e))

    # write result
    for data, name, mode in result:
        outname = opts.output or name
        if outname == "-":
            sys.stdout.write(data)
        else:
            try:
                with open(outname, mode) as fout:
                    fout.write(data)
            except IOError as e:
                    sys.exit("Error: " + str(e))

    # return status
    return rc

if __name__ == "__main__":
    status = main()
    sys.exit(status)
