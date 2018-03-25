#!/usr/bin/env python

import sys

if sys.version_info < (3, 6, 0):
    sys.stderr.write("You need python 3.6 or later to run this script\n")
    sys.exit(1)

from pathlib import Path
import argparse


gc_args = None


def retrieve_args():
    parser = argparse.ArgumentParser(description='''
    Trace locking by commenting printf() lines, trace unlocking by uncommenting them.
    ''')

    parser.add_argument('trace_lock',
                    help='on: Comment out trace statements, off: uncomment')

    rg = parser.parse_args()


def main():
    global gc_args

    gc_args = retrieve_args()

if __name__ == '__main__':
    main()
