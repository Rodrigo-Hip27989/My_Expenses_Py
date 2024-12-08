class Path:
    def __init__(self, path, is_export, is_import):
        self._path = path
        self._is_export = is_export
        self._is_import = is_import

    @property
    def path(self):
        return self._path

    @property
    def is_export(self):
        return self._is_export

    @property
    def is_import(self):
        return self._is_import

    @path.setter
    def path(self, path):
        self._path = path

    @is_export.setter
    def is_export(self, is_export):
        self._is_export = is_export

    @is_import.setter
    def is_import(self, is_import):
        self._is_import = is_import

    def get_db_values(self):
        return [self._path, self._is_export, self._is_import]

    def __str__(self):
        return (f"Path: {self._path()}\n"
                f"Is Export: {self._is_export}\n"
                f"Is_Import: {self._is_import}")
