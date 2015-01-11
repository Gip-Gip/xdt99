#!/usr/bin/env python

import os

from config import Dirs, Disks, Files
from utils import xas, xdm, error, checkFilesEq


### Check function

def checkImageFilesEq(name, genfile, reffile):
    """check if non-zero bytes in binary files are equal"""
    with open(genfile, "rb") as fg, open(reffile, "rb") as fr:
        genimage = fg.read()
        refimage = fr.read()
    if len(genimage) != len(refimage):
        error("Object code", "Image length mismatch: " + name)
    # TI-generated images may contain arbitrary bytes in BSS segments
    for i in xrange(len(genimage)):
        if genimage[i] != "\x00" and genimage[i] != refimage[i]:
            error("Object code", "Image contents mismatch " + name +
                  " @ " + hex(i))


### Main test

def runtest():
    """check cross-generated output against native reference files"""

    # object code
    for infile, opts, reffile in [
            ("asdirs.asm", [], "ASDIRS-O"),
            ("asorgs.asm", [], "ASORGS-O"),
            ("asopcs.asm", [], "ASOPCS-O"),
            ("asexprs.asm", [], "ASEXPRS-O"),
            ("asbss.asm", [], "ASBSS-O"),
            ("asregs.asm", ["-OR"], "ASREGS-O"),
            ("ashello.asm", ["-OR"], "ASHELLO-O"),
            ("ascopy.asm", [], "ASCOPY-O"),
            ("ascopyn.asm", [], "ASCOPYN-O"),
            ("assize1.asm", [], "ASSIZE1-O"),
            ("assize2.asm", [], "ASSIZE2-O"),
            ("assize3.asm", [], "ASSIZE3-O"),
            ("assize4.asm", [], "ASSIZE4-O"),
            ("astisym.asm", [], "ASTISYM-O"),
            ("asimg1.asm", [], "ASIMG1-O"),
            ("asimg2.asm", [], "ASIMG2-O"),
            ("asimg3.asm", [], "ASIMG3-OX"),
            ("ascart.asm", ["-OR"], "ASCART-O"),
            ("asxext.asm", ["-OR"], "ASXEXT-O")
            ]:
        source = os.path.join(Dirs.sources, infile)
        xas(*[source] + opts + ["-o", Files.output])
        xdm(Disks.asmsrcs, "-e", reffile, "-o", Files.reference)
        checkFilesEq("Object code", Files.output, Files.reference, fmt="DF80")

    # image files
    for infile, opts, reffile in [
            ("ashello.asm", ["-OR"], "ASHELLO-I"),
            ("astisym.asm", [], "ASTISYM-I"),
            ("asimg1.asm", [], "ASIMG1-I"),
            ("asimg2.asm", [], "ASIMG2-I"),
            ("asimg3.asm", [], "ASIMG3-I")
            ]:
        source = os.path.join(Dirs.sources, infile)
        xas(*[source] + opts + ["-i", "-o", Files.output])
        xdm(Disks.asmsrcs, "-e", reffile, "-o", Files.reference)
        checkImageFilesEq(infile, Files.output, Files.reference)

    # cleanup
    os.remove(Files.output)
    os.remove(Files.reference)


if __name__ == "__main__":
    runtest()
