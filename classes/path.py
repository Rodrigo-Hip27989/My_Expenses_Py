class Path:
    def __init__(self, path, is_export, is_import):
        self.path = path
        self.is_export = is_export
        self.is_import = is_import

    # Getters
    def get_path(self):
        return self.path

    def get_is_export(self):
        return self.is_export

    def get_is_import(self):
        return self.is_import

    # Setters
    def set_path(self, path):
        self._path = path

    def set_is_export(self, is_export):
        self.is_export = is_export

    def set_is_import(self, is_import):
        self.is_import = is_import

    def get_db_values(self):
        return [self.path, self.is_export, self.is_import]

    def __str__(self):
        return (f"Path: {self.get_path()}\n"
                f"Is Export: {self.get_is_export()}\n"
                f"Is_Import: {self.get_is_import()}")
