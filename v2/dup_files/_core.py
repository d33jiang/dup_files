import abc
import os
import typing

__all__ = (
    'FileDigest',
    'FileGrouper',

    'PathType',
    'DigestType',
)

StringLike = typing.Union[str, bytes]
PathType = typing.Union[StringLike, os.PathLike]

DigestType = typing.Any


class FileDigest(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def process(self, file_path: PathType) -> DigestType:
        raise NotImplementedError

    def __call__(self, file_path: PathType) -> DigestType:
        return self.process(file_path)


class FileGrouper(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def group(self, file_paths: typing.Iterable[PathType]) -> typing.Iterable[list[PathType]]:
        raise NotImplementedError
