from __future__ import annotations

import h5py


class LH5DecodeError(Exception):
    def __init__(self, message: str, file: str, obj: str) -> None:
        super().__init__(message)

        self.file = file.filename if isinstance(file, h5py.File) else file
        self.obj = obj

    def __str__(self) -> str:
        return (
            f"while reading object '{self.obj}' in file {self.file}: "
            + super().__str__()
        )


class LH5EncodeError(Exception):
    def __init__(
        self, message: str, file: str | h5py.File, group: str | h5py.Group, name: str
    ) -> None:
        super().__init__(message)

        self.file = file.filename if isinstance(file, h5py.File) else file
        self.group = (group.name if isinstance(file, h5py.File) else group).rstrip("/")
        self.name = name.lstrip("/")

    def __str__(self) -> str:
        return (
            f"while writing object {self.group}/{self.name} to file {self.file}: "
            + super().__str__()
        )
