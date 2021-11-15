import os

class i_filer:
    def get_dir(self, dir_path: str) -> str:
        """
        Gets or generate a directory from the path.
        :param dir_path: a relative path based on root path
        :return: the final existed directory path
        """
        pass

    def get_file(self, file_path) -> str:
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


class filer(i_filer):
    def __init__(self):
        super().__init__()
        self._root_path = ""

    def get_dir(self, dir_path: str) -> str:
        full = f"{self.root_path}/{dir_path}"
        if not os.path.exists(full):
            os.makedirs(full, exist_ok=True)
        return full

    def get_file(self, file_path) -> str:
        full = f"{self.root_path}/{file_path}"
        if not os.path.exists(full):
            folder, file = os.path.split(full)
            os.makedirs(folder, exist_ok=True)
            if not os.path.exists(file):
                with open(full, "w"):
                    pass
        return full

    @property
    def root_path(self) -> str:
        return self._root_path

    @root_path.setter
    def root_path(self, value: str):
        self._root_path = value
