import os
from typing import List, Callable, Iterable

sep = os.sep


class FileSystemInfo:
    def __init__(self):
        self.FullPath = ""
        self.Folder = ""
        self.Name = ""

    def __str__(self):
        return self.FullPath

    def __repr__(self):
        return self.FullPath

    @property
    def IsExisted(self) -> bool:
        return os.path.exists(self.FullPath)


class File(FileSystemInfo):
    def __init__(self, full_path):
        super().__init__()
        self.FullPath = full_path
        self.Folder, self.FullName = os.path.split(full_path)
        self.ParentDirectory: "Directory" = Directory(self.Folder)
        self.Name, self.Extension = os.path.splitext(self.FullPath)

    def CreateOrTruncate(self):
        self.ParentDirectory.Create()
        with open(self.FullPath, "w", encoding="utf-8"):
            pass


Filter = Callable[[str], bool]


def All(file_or_folder_name: str) -> bool:
    return True


def EndsWith(extension: str) -> Filter:
    def func(file_name: str):
        return file_name.endswith(extension)

    return func


class Directory(FileSystemInfo):
    def __init__(self, full_path):
        super().__init__()
        self.FullPath = full_path
        self.Folder, self.Name = os.path.split(full_path)

    def Create(self):
        os.makedirs(self.FullPath, exist_ok=True)

    @property
    def FilesIt(self) -> Iterable[File]:
        for root, ds, fs in os.walk(self.FullPath):
            for f in fs:
                yield File(f"{root}{sep}{f}")

    @property
    def DirectoriesIt(self) -> Iterable["Directory"]:
        for root, ds, fs in os.walk(self.FullPath):
            for d in ds:
                yield Directory(f"{root}{sep}{d}")

    @property
    def Files(self) -> List[File]:
        return [File(f"{root}{sep}{f}") for root, ds, fs in os.walk(self.FullPath) for f in fs]

    @property
    def Directories(self) -> List["Directory"]:
        return [Directory(f"{root}{sep}{d}") for root, ds, fs in os.walk(self.FullPath) for d in ds]

    def GetSubFiles(self, _filter: Filter = All) -> List[File]:
        return [f for f in self.FilesIt if _filter(f.FullName)]

    def GetSubDirectories(self, _filter: Filter = All) -> List["Directory"]:
        return [d for d in self.DirectoriesIt if _filter(d.Name)]

    def GetSubFilesIt(self, _filter: Filter = All) -> Iterable[File]:
        for f in self.FilesIt:
            if _filter(f.FullName):
                yield f

    def GetSubDirectoriesIt(self, _filter: Filter = All) -> Iterable["Directory"]:
        for d in self.DirectoriesIt:
            if _filter(d.Name):
                yield d

    def SubFile(self, fileName) -> File:
        return File(f"{self.FullPath}{sep}{fileName}")

    def SubDirectory(self, folderName) -> "Directory":
        return Directory(f"{self.FullPath}{sep}{folderName}")
