import os

from ._core import FileDigest, PathType

__all__ = (
    'FileSize',
    'HashlibDigestGroup',
)


class FileSize(FileDigest):

    def process(self, file_path: PathType) -> int:
        return os.stat(file_path).st_size


class HashlibDigestGroup(FileDigest):
    DEFAULT_BUFFER_SIZE = 4096

    def __init__(self, *message_digest_init_functions, buffer_size: int = DEFAULT_BUFFER_SIZE):
        self._md_init_funcs = message_digest_init_functions
        self._buffer_size = buffer_size

    def process(self, file_path: PathType) -> bytes:
        mds = [
            md_init()
            for md_init in self._md_init_funcs
        ]

        with open(file_path, 'rb') as file_in:
            buf = file_in.read(self._buffer_size)
            while len(buf) > 0:
                for md in mds:
                    md.update(buf)
                buf = file_in.read(self._buffer_size)

        return b''.join(
            md.digest()
            for md in mds
        )
