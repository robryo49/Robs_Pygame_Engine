

class Music:
    def __init__(self, name: str, path: str):
        self._name = name
        self._path = path

    # region PROPERTIES

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    # endregion

    def __str__(self) -> str:
        return f"Music({self._name})"
