import hashlib
import os.path

import dup_files
from dup_files import PathType, DigestType, digests, groupers

detector = dup_files.DuplicatesDetector.create_from_root_dir('D:\\temp')


def dump_state():
    print('File Classes')
    for group in detector.file_classes:
        print(f'- {group}')
    print()

    print('Singletons')
    print(detector.singletons)
    print()


print('# Initial State')
dump_state()
print()


class BasicNameChecksum(dup_files.FileDigest):

    def process(self, file_path: PathType) -> DigestType:
        file_name = os.path.basename(file_path)
        return sum(bytearray(file_name, 'utf-8')) % 8


def main():
    if True:
        basic_name_checksum = BasicNameChecksum()

        print('# Naive Name Checksum Results')
        for group in detector.file_classes:
            for file_path in group:
                print(basic_name_checksum.process(file_path), file_path)
        print()

        print('# Group by Naive Name Checksum')
        detector.group_by_digest(basic_name_checksum)
        dump_state()
        print()

    if True:
        print('# Group by File Size')
        detector.group_by_digest(digests.FileSize())
        dump_state()
        print()

    if True:
        print('# Group by Hashes')
        detector.group_by_digest(digests.HashlibDigestGroup(hashlib.md5, hashlib.sha1, hashlib.sha256))
        dump_state()
        print()

    if True:
        print('# Group by File Content')
        detector.group_by(groupers.GroupByContent())
        dump_state()
        print()


main()
