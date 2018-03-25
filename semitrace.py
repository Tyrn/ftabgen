#!/usr/bin/env python

import sys

if sys.version_info < (3, 6, 0):
    sys.stderr.write("You need python 3.6 or later to run this script\n")
    sys.exit(1)

from pathlib import Path
import argparse
import re

gc_args       = None
g_src         = 'Src'
gc_ini        = r"\binitialise_monitor_handles\b"
gc_std_set    = (
                r"\bprintf\b"
                r"|\bscanf\b"
)
gc_dslash_ex  = re.compile(r"^\s*\/\/")
gc_ini_ex     = re.compile(gc_ini)
gc_std_ex     = re.compile(gc_std_set)
gc_all_ex     = re.compile(gc_ini + '|' + gc_std_set)

gc_arg_set    = ['on', 'off', 'remove', 'removeall']

def consume_line(line):
    if gc_args.trace_on == gc_arg_set[0]: # on:        Remove comments, if any.
        if gc_all_ex.findall(line) and gc_dslash_ex.match(line):
            return gc_dslash_ex.sub("", line, 1)
        return line
    if gc_args.trace_on == gc_arg_set[1]: # off:       Comment out, if not commented.
        if gc_all_ex.findall(line) and not gc_dslash_ex.match(line):
            return '//' + line
        return line
    if gc_args.trace_on == gc_arg_set[2]: # remove:    Remove uncommented std lines.
        return line
    if gc_args.trace_on == gc_arg_set[3]: # removeall: Remove every std line.
        return line
    return line


def check_file(path):
    print(f'\n*** {str(path)}\n')
    with open(path, "r") as f:
      for line in f.readlines():
          o_line = consume_line(line)
          if gc_all_ex.findall(o_line):
              print(o_line)


def check_sources():
    src = Path(g_src)
    if src.is_dir():
      for i in src.glob('*.c'):
          if i.is_file():
              check_file(i)


def retrieve_args():
    parser = argparse.ArgumentParser(description='''
    Trace enabled by uncommenting printf() lines, disabled by commenting them.
    ''')

    parser.add_argument('trace_on',
                    help='on: Comment out trace statements, off: uncomment')

    rg = parser.parse_args()
    return rg


def main():
    global gc_args

    gc_args = retrieve_args()

    if gc_args.trace_on not in gc_arg_set:
        print(f'Unrecognized option "{gc_args.trace_on}"')
        sys.exit()

    check_sources()

if __name__ == '__main__':
    main()
