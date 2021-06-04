import collections
import typing

from ._core import FileDigest, FileGrouper, PathType

__all__ = (
    'GroupByDigest',
    'GroupByContent',
)


class GroupByDigest(FileGrouper):

    def __init__(self, digest: FileDigest):
        self._digest = digest

    def group(self, file_paths: typing.Iterable[PathType]) -> typing.Iterable[list[PathType]]:
        return _group_by(file_paths, self._digest)


_TV = typing.TypeVar('_TV')


def _group_by(xs: typing.Iterable[_TV], func: typing.Callable[[_TV], typing.Hashable]) \
        -> typing.Iterable[list[_TV]]:
    mm = collections.defaultdict(list)
    for x in xs:
        mm[func(x)].append(x)

    return mm.values()


class GroupByContent(FileGrouper):
    DEFAULT_BUFFER_SIZE = 4096

    def __init__(self, buffer_size: int = DEFAULT_BUFFER_SIZE):
        self._buffer_size = buffer_size

    def group(self, file_paths: typing.Iterable[PathType], acc=None) -> typing.Iterable[list[PathType]]:
        if acc is None:
            acc = []

        while len(file_paths) > 1:
            rep_file = file_paths[0]

            rep_list = [rep_file]
            oth_list = []

            # Handle each file individually for spatial locality
            for file in file_paths[1:]:
                (rep_list if self._test_file_equality(rep_file, file) else oth_list).append(file)

            acc.append(rep_list)
            file_paths = oth_list

        if len(file_paths) == 1:
            acc.append(file_paths)

        return acc

    def _test_file_equality(self, path_rep, path_oth):
        buffer_size = self._buffer_size

        with open(path_rep, 'rb') as file_rep, open(path_oth, 'rb') as file_oth:
            buf_rep = file_rep.read(buffer_size)
            buf_oth = file_oth.read(buffer_size)

            while len(buf_rep) == len(buf_oth) > 0 and buf_rep == buf_oth:
                buf_rep = file_rep.read(buffer_size)
                buf_oth = file_oth.read(buffer_size)

            if len(buf_rep) != len(buf_oth):
                # Buffers do not match
                return False
            else:
                # If true, both EOFs reached and the files match
                # Otherwise, buffers do not match since the while-loop condition was False
                return len(buf_rep) == 0
