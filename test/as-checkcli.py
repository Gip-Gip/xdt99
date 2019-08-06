#!/usr/bin/env python

import os
import re

from config import Dirs, Disks, Files
from utils import (chrw, ordw, xas, xdm, error, content, content_len, check_obj_code_eq,
                   check_image_files_eq, check_list_files_eq)


def remove(files):
    for fn in files:
        if os.path.exists(fn):
            os.remove(fn)


# Check functions

def check_exists(files):
    for fn in files:
        try:
            with open(fn, "rb") as f:
                x = f.read()[0]
        except (IOError, IndexError):
            error("Files", "File missing or empty: " + fn)


def check_bin_text_equal_bytes(outfile, reffile):
    with open(outfile, "r") as fout, open(reffile, "rb") as fref:
        txt = " ".join(fout.readlines())
        bin = fref.read()
    data = [b for b in bin]
    dirs = [int(m, 16) for m in re.findall(">([0-9A-Fa-f]{2})", txt)][1:]  # skip AORG
    if data != dirs:
        error("DATA", "DATA/word mismatch")


def check_bin_text_equal_words(outfile, reffile):
    with open(outfile, "r") as fout, open(reffile, "rb") as fref:
        txt = " ".join(fout.readlines())
        bin = fref.read()
    if len(bin) % 2 == 1:
        bin += b"\x00"
    data = [ordw(bin[i:i + 2]) for i in range(0, len(bin), 2)]
    dirs = [int(m, 16) for m in re.findall(">([0-9A-Fa-f]{4})", txt)][1:]  # skip AORG
    if data != dirs:
        error("DATA", "DATA/word mismatch")


def check_instructions(outfile, instr):
    with open(outfile, "r") as fout:
        txt = fout.readlines()
    condensed = [line.replace(" ", "").strip() for line in txt if line.strip()]
    for i, line in enumerate(condensed):
        if (not ((instr[i][0] == 'b' and (line[:4] == instr[i])) or
                 line == instr[i])):
            error("text", "Malformed text file")


def check_symbols(outfile, symbols):
    """check if all symbol/value pairs are in symfile"""
    with open(outfile, "r") as fout:
        source = fout.readlines()
    equs = {}
    for i in range(0, len(source), 2):
        sym = source[i].split(':')[0]
        val = source[i + 1].upper().split("EQU", 1)[1].strip().split()[0]
        equs[sym] = val
    for sym, val in symbols:
        if equs.get(sym) != val:
            error("symbols", f"Symbol mismatch for {sym}={val}/{equs.get(sym)}")


# Main test

def runtest():
    """check command line interface"""

    # input and output files
    source = os.path.join(Dirs.sources, "ashello.asm")
    with open(Files.output, "wb") as f:
        xas(source, "-R", "-o", "-", stdout=f)
    xdm(Disks.asmsrcs, "-e", "ASHELLO-O", "-o", Files.reference)
    check_obj_code_eq(Files.output, Files.reference)

    with open(Files.output, "wb") as f:
        xas(source, "-R", "-i", "-o", "-", stdout=f)
    xdm(Disks.asmsrcs, "-e", "ASHELLO-I", "-o", Files.reference)
    check_image_files_eq(Files.output, Files.reference)

    with open(Files.output, "w") as f:
        xas(source, "-R", "-o", Files.output, "-L", "-", stdout=f)
    xdm(Disks.asmsrcs, "-e", "ASHELLO-L", "-o", Files.reference)
    check_list_files_eq(Files.output, Files.reference)

    source = os.path.join(Dirs.sources, "nonexisting")
    with open(Files.error, "w") as ferr:
        xas(source, "-i", "-R", "-o", Files.output, stderr=ferr, rc=1)
    with open(Files.error, "r") as ferr:
        errs = ferr.readlines()
    if len(errs) != 1 or errs[0][:10] != "File error":
        error("File error", "Incorrect file error message")

    # include path
    source = os.path.join(Dirs.sources, "ascopyi.asm")
    incls = os.path.join(Dirs.sources, "test") + "," + \
        os.path.join(Dirs.sources, "test", "test")
    xas(source, "-i", "-I", incls, "-o", Files.output)
    with open(Files.output, "rb") as f:
        data = f.read()
    if len(data[6:]) != 20:
        error("Include paths", "Incorrect image length")

    # command-line definitions
    source = os.path.join(Dirs.sources, "asdef.asm")
    xas(source, "-b", "-D", "s1=1", "s3=3", "s2=4", "-o", Files.output)
    assert content(Files.output) == b"\x01\x03"
    xas(source, "-b", "-D", "s1=2,s2=2,s3=3", "-o", Files.output)
    assert content(Files.output) == b"\x02\x03"

    # various parameter combinations
    source = os.path.join(Dirs.sources, "asxbank1.asm")
    remove([Files.reference])
    xas(source, "-b", "-o", Files.output, "-L", Files.reference)
    check_exists([Files.reference])

    # text data output
    source = os.path.join(Dirs.sources, "ascart.asm")
    xas(source, "-b", "-R", "-o", Files.reference)
    xas(source, "-t", "a2", "-R", "-o", Files.output)
    check_bin_text_equal_bytes(Files.output, Files.reference)

    source = os.path.join(Dirs.sources, "asmtext.asm")
    xas(source, "-t", "a2", "-R", "-o", Files.output)
    check_instructions(Files.output,
                       [";aorg>1000", "byte", ";aorg>2000", "byte"])

    # symbols
    source = os.path.join(Dirs.sources, "assyms.asm")
    xas(source, "-b", "-R", "-o", Files.reference, "-E", Files.output)
    check_symbols(Files.output,
                  (("START", ">0000"), ("S1", ">0001"), ("S2", ">0018"),
                  ("VDPWA", ">8C02")))

    # disable warnings
    source = os.path.join(Dirs.sources, "aswarn.asm")
    with open(Files.error, "w") as ferr:
        xas(source, "-b", "-R", "-w", "-o", Files.output, stderr=ferr, rc=0)
    if content_len(Files.error) > 0:
        error("warn", "warnings, even though disabled")

    # cleanup
    os.remove(Files.output)
    os.remove(Files.reference)
    os.remove(Files.error)


if __name__ == "__main__":
    runtest()
    print("OK")
