#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    Script to rename movies files to a more standard name
"""

from __future__ import print_function

import os
import re
import sys


if len(sys.argv) != 3:
    print('''Script to get rid of garbage in movies names''')
    print('''Usage: rename_shows.py /path/to/files "My show Name"''')
    print('''   "path" may contain subdirectories, in which case each one will be processed''')
    print('''   "My Show Name" is used as a regex to rename files to "My Show Name E01E01.mkv"''')

my_dir = sys.argv[1]
name = sys.argv[2]


print(my_dir)
print(name)

choice = raw_input('Is this OK (y/n)? ')
if choice != 'y':
    sys.exit(0)

regexp = '.*' + '.*'.join(name.split()) + r'.*(s\d+e\d+).*\.(m4v|mp4|mkv|avi)'


def rename(path):
    for i in os.listdir(path):
        if os.path.isfile(path + '/' + i):
            old_name = i
            match = re.match(regexp, old_name, re.IGNORECASE)
            if not match:
                print('WARNING: not renaming ' + old_name)
                continue

            new_name = name + ' ' + match.groups()[0].upper() + '.' + match.groups()[1]

            os.rename(path + '/' + old_name, path + '/' + new_name)
        elif os.path.isdir(path + '/' + i):
            next_dir = os.path.join(path, i)
            rename(next_dir)


rename(my_dir)

print('DONE')
