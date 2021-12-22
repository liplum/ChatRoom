from files import Directory, File, sep


class ifiler:
    def get_dir(self, dir_path: str) -> Directory:
        """
        Gets or generate a directory from the path.
        :param dir_path: a relative path based on root path
        :return: the final existed directory path
        """
        pass

    def get_file(self, file_path) -> File:
        """
        Gets or generate a file from the path.
        :param file_path: a relative path based on root path
        :return: the final existed file path
        """
        pass

    @property
    def root_path(self) -> str:
        return ""

    @root_path.setter
    def root_path(self, value: str):
        pass


class filer(ifiler):
    def __init__(self):
        super().__init__()
        self._root_path = ""

    def get_dir(self, dir_path: str) -> Directory:
        dire = Directory(f"{self.root_path}{sep}{dir_path}")
        if not dire.IsExisted:
            dire.Create()
        return dire

    def get_file(self, file_path) -> File:
        f = File(f"{self.root_path}{sep}{file_path}")
        if not f.IsExisted:
            f.CreateOrTruncate()
        return f

    @property
    def root_path(self) -> str:
        return self._root_path

    @root_path.setter
    def root_path(self, value: str):
        self._root_path = value
