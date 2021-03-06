#!/usr/bin/env python

import os
import shutil
import datetime

from config import Dirs, Disks, Files, Masks
from utils import xdm, check_files_eq, check_file_matches


def tiname(s):
    """create TI filename from local filename"""
    return os.path.splitext(os.path.basename(s))[0][:10].upper()


# Main test

def runtest():
    """compare extracted files to reference files"""

    # compare with reference files generated by TI Image Tool
    shutil.copyfile(Disks.recsdis, Disks.work)
    for fn in ['V1', 'V16', 'V126', 'V127', 'V128', 'V254', 'V10R',
               'V64V', 'V255V1', 'V255V2', 'V255V3', 'V255V4', 'V255V5',
               # NOTE: F1.tfi has incorrect record count
               'F16', 'F127', 'F128', 'F129', 'F254', 'F255', 'F64V', 'F10R']:
        xdm(Disks.work, '-e', fn, '-t', '-o', Files.output)
        check_files_eq('TIFiles', Files.output, os.path.join(Dirs.refs, fn + '.tfi'), 'PROGRAM', Masks.TIFile)

    # compare with reference files generated by Classic99
    for fn in ['V16', 'V127', 'V64V', 'V10R', 'F129', 'F64V', 'F10R']:
        xdm(Disks.work, '-e', fn, '-9', '-o', Files.output)
        check_files_eq('v9t9', Files.output, os.path.join(Dirs.refs, fn + '.v9t9'), 'PROGRAM', Masks.v9t9)
        xdm('-F', Files.output, '-9', '-o', Files.output)
        xdm(Disks.work, '-e', fn, '-o', Files.reference)
        check_files_eq('v9t9', Files.output, Files.reference, 'DV')

    # compare files extracted from fragmented image
    shutil.copyfile(Disks.frag, Disks.work)
    for fn in ['F1', 'F6']:
        xdm(Disks.work, '-e', fn, '-o', Files.output)
        check_files_eq('Frag Disk', Files.output,
                     os.path.join(Dirs.refs, 'FRAG' + fn), 'DIS/VAR127')
    xdm(Disks.work, '-d', 'F1')
    xdm(Disks.work, '-e', 'F6', '-o', Files.output)
    check_files_eq('Frag Disk', Files.output, os.path.join(Dirs.refs, 'FRAGF6'), 'DIS/VAR127')
    shutil.copyfile(Disks.frag, Disks.work)
    xdm(Disks.work, '-a', Files.output, '-n', 'COPY', '-f', 'DIS/VAR127')
    xdm(Disks.work, '-e', 'F1', '-o', Files.output)
    check_files_eq('Frag Disk', Files.output, os.path.join(Dirs.refs, 'FRAGF1'), 'DIS/VAR127')

    # compare short and long TIFiles
    rfile = os.path.join(Dirs.refs, 'V64V')
    shutil.copyfile(rfile, Files.reference)
    with open(Files.output, 'w') as f:
        xdm('-I', Files.reference, stdout=f)
    check_file_matches(Files.output, [(0, r'{:10s}'.format(tiname(Files.reference)) +
                                       r'\s+4  DIS/VAR 64\s+575 B\s+9 recs\s+[\d:\- ]+M')])
    xdm(Disks.work, '-X', 'sssd', '-t', '-a', rfile)
    xdm(Disks.work, '-e', 'V64V', '-o', Files.output)
    xdm('-F', rfile, '-o', Files.reference)
    check_files_eq('Short TIFiles', Files.output, Files.reference, 'DIS/VAR64')

    # cleanup
    os.remove(Files.output)
    os.remove(Disks.work)


if __name__ == '__main__':
    runtest()
    print('OK')
