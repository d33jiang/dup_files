"""
Created on Sep 26, 2018
@author: David Jiang
"""

# Imports

import hashlib
import os
from collections import defaultdict


# Filters

def get_file_size(file_path):
    return os.stat(file_path).st_size


def get_hashes_func(file_path, md_init_funcs):
    mds = [md_init() for md_init in md_init_funcs]
    with open(file_path, 'rb') as fd:
        buf = fd.read(HASH_BUFFER_SIZE)
        while len(buf) > 0:
            for md in mds:
                md.update(buf)
            buf = fd.read(HASH_BUFFER_SIZE)

    return b''.join(
        md.digest()
        for md in mds
    )


def get_hashes(*md_init_funcs):
    return lambda file_path: get_hashes_func(file_path, md_init_funcs)


# Configuration

DIR_ROOT = 'D:\\testDirectory'

PERFORM_FULL_COMPARISON = True

HASH_BUFFER_SIZE = 4896
COMPARE_BUFFER_SIZE = 4096

DIGESTS = [get_file_size, get_hashes(hashlib.md5, hashlib.sha1, hashlib.sha256)]


#
# Development Testing

# # For testing purposes only
# def name_checksum(x):
#     return sum(bytearray(x, 'utf-8')) % 8
#
# DIGESTS = [name_checksum]
# print(get_hashes(hashlib.md5)("D:\\testDirectory\\odeToJoy.mid"))
# DIGESTS = []


# Logic

# > Definition(s)

def reduce(fll):
    return [fl for fl in fll if len(fl) > 1]


# > Directory Tree Traversal

file_classes = [
    [
        os.path.join(root, file)
        for root, _, files in os.walk(DIR_ROOT)
        for file in files
    ]
]


# > Distinction by Digests

def group_by(xs, func):
    mm = defaultdict(list)
    for x in xs:
        mm[func(x)].append(x)

    return mm.values()


for digest in DIGESTS:
    file_classes = reduce(
        [
            file_set
            for fl in file_classes
            for file_set in group_by(fl, digest)
        ]
    )


# > Distinction by Full Comparisons

def file_equal(path1, path2):
    with open(path1, 'rb') as fd_rep, open(path2, 'rb') as fd_oth:
        buf_rep = fd_rep.read(COMPARE_BUFFER_SIZE)
        buf_oth = fd_oth.read(COMPARE_BUFFER_SIZE)

        while len(buf_rep) == len(buf_oth) > 0 and buf_rep == buf_oth:
            buf_rep = fd_rep.read(COMPARE_BUFFER_SIZE)
            buf_oth = fd_oth.read(COMPARE_BUFFER_SIZE)

        if len(buf_rep) != len(buf_oth):
            return False  # Buffers do not match
        else:
            return len(buf_rep) == 0  # If true, both EOFs reached; otherwise, buffers do not match


def group_by_full_comparison(file_list, acc=None):
    if acc is None:
        acc = []

    while len(file_list) > 1:
        rep_file = file_list[0]

        rep_list = [rep_file]
        oth_list = []

        for file in file_list[1:]:  # Handle each file individually for spatial locality
            (rep_list if file_equal(rep_file, file) else oth_list).append(file)

        acc.append(rep_list)
        file_list = oth_list

    if len(file_list) == 1:
        acc.append(file_list)

    return acc


if PERFORM_FULL_COMPARISON:
    file_classes = reduce(
        [
            file_set
            for fl in file_classes
            for file_set in group_by_full_comparison(fl)
        ]
    )
