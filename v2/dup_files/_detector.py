import os
import typing

from ._core import FileDigest, FileGrouper, PathType
from .groupers import GroupByDigest

__all__ = (
    'DuplicatesDetector',
)


class DuplicatesDetector:
    FileClass = typing.Sequence[PathType]

    def __init__(self, *file_classes: FileClass, keep_singletons: bool = True):
        self._keep_singletons = keep_singletons

        self.file_classes = list(file_classes)
        self.singletons = []

        self._filter_singletons()

    @staticmethod
    def create_from_root_dir(root_dir_path: PathType) -> 'DuplicatesDetector':
        return DuplicatesDetector(
            list(
                os.path.join(root, file)
                for root, _, files in os.walk(root_dir_path)
                for file in files
            )
        )

    def _filter_singletons(self):
        if self._keep_singletons:
            # Keep singletons
            file_classes = self.file_classes
            self.file_classes = []

            for fc in file_classes:
                if len(fc) == 1:
                    self.singletons.append(fc[0])
                else:
                    self.file_classes.append(fc)
        else:
            # Drop singletons (v1 logic)
            self.file_classes = [
                group
                for group in self.file_classes
                if len(group) > 1
            ]

    def group_by_digest(self, digest: FileDigest):
        self.group_by(GroupByDigest(digest))

    def group_by(self, grouper: FileGrouper):
        self.file_classes = list(
            file_class
            for old_file_class in self.file_classes
            for file_class in grouper.group(old_file_class)
        )

        self._filter_singletons()
