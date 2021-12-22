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
        self.Folder, self.Full_name = os.path.split(full_path)
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
    def Files(self) -> Iterable[File]:
        for root, ds, fs in os.walk(self.FullPath):
            for f in fs:
                yield File(f"{root}{sep}{f}")

    @property
    def Directories(self) -> Iterable["Directory"]:
        for root, ds, fs in os.walk(self.FullPath):
            for d in ds:
                yield Directory(f"{root}{sep}{d}")

    def GetSubFiles(self, _filter: Filter = All) -> List[File]:
        return [f for f in self.Files if _filter(f.Name)]

    def GetSubDirectories(self, _filter: Filter = All) -> List["Directory"]:
        return [d for d in self.Directories if _filter(d.Name)]

    def SubFile(self, fileName) -> File:
        return File(f"{self.FullPath}{sep}{fileName}")

    def SubDirectory(self, folderName) -> "Directory":
        return Directory(f"{self.FullPath}{sep}{folderName}")
