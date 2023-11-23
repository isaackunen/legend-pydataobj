from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .. import lgdo_utils as utils
from .array import Array
from .lgdo import LGDO
from .scalar import Scalar
from .vectorofvectors import VectorOfVectors


class VectorOfEncodedVectors(LGDO):
    """An array of variable-length encoded arrays.

    Used to represent an encoded :class:`.VectorOfVectors`. In addition to an
    internal :class:`.VectorOfVectors` `self.encoded_data` storing the encoded
    data, a 1D :class:`.Array` in `self.encoded_size` holds the original sizes
    of the encoded vectors.

    See Also
    --------
    .VectorOfVectors
    """

    def __init__(
        self,
        encoded_data: VectorOfVectors = None,
        decoded_size: Array = None,
        attrs: dict[str, Any] = None,
    ) -> None:
        """
        Parameters
        ----------
        encoded_data
            the vector of encoded vectors.
        decoded_size
            an array holding the original length of each encoded vector in
            `encoded_data`.
        attrs
            A set of user attributes to be carried along with this LGDO. Should
            include information about the codec used to encode the data.
        """
        if isinstance(encoded_data, VectorOfVectors):
            self.encoded_data = encoded_data
        elif encoded_data is None:
            self.encoded_data = VectorOfVectors(dtype="ubyte")
        else:
            raise ValueError("encoded_data must be a valid VectorOfVectors")

        if isinstance(decoded_size, Array):
            self.decoded_size = decoded_size
        elif decoded_size is not None:
            self.decoded_size = Array(decoded_size)
        elif encoded_data is not None:
            self.decoded_size = Array(
                shape=len(encoded_data), dtype="uint32", fill_val=0
            )
        elif decoded_size is None:
            self.decoded_size = Array()

        if len(self.encoded_data) != len(self.decoded_size):
            raise RuntimeError("encoded_data vs. decoded_size shape mismatch")

        super().__init__(attrs)

    def datatype_name(self) -> str:
        return "array"

    def form_datatype(self) -> str:
        et = utils.get_element_type(self.encoded_data)
        return "array<1>{encoded_array<1>{" + et + "}}"

    def __len__(self) -> int:
        return len(self.encoded_data)

    def __eq__(self, other: VectorOfEncodedVectors) -> bool:
        if isinstance(other, VectorOfEncodedVectors):
            return (
                self.encoded_data == other.encoded_data
                and self.decoded_size == other.decoded_size
                and self.attrs == other.attrs
            )

        else:
            return False

    def resize(self, new_size: int) -> None:
        """Resize vector along the first axis.

        See Also
        --------
        .VectorOfVectors.resize
        """
        self.encoded_data.resize(new_size)
        self.decoded_size.resize(new_size)

    def __getitem__(self, i: int) -> tuple[NDArray, int]:
        """Return vector at index `i`.

        Returns
        -------
        (encoded_data, decoded_size)
            the encoded array and its decoded length.
        """
        return (self.encoded_data[i], self.decoded_size[i])

    def __iter__(self) -> Iterator[tuple[NDArray, int]]:
        yield from zip(self.encoded_data, self.decoded_size)

    def __str__(self) -> str:
        string = ""
        pos = 0
        for vec, size in self:
            vec = vec.to_numpy()
            if pos != 0:
                string += " "

            string += (
                np.array2string(
                    vec,
                    prefix=" ",
                    formatter={
                        "int": lambda x, vec=vec: f"0x{x:02x}"
                        if vec.dtype == np.ubyte
                        else str(x)
                    },
                )
                + f" decoded_size = {size}"
            )

            if pos < len(self.encoded_data.cumulative_length):
                string += ",\n"

            pos += 1

        string = f"[{string}]"

        attrs = self.getattrs()
        if len(attrs) > 0:
            string += f" with attrs={attrs}"

        return string

    def __repr__(self) -> str:
        npopt = np.get_printoptions()
        np.set_printoptions(
            threshold=5,
            edgeitems=2,
            linewidth=100,
        )
        out = (
            "VectorOfEncodedVectors(encoded_data="
            + repr(self.encoded_data)
            + ", decoded_size="
            + repr(self.decoded_size)
            + ", attrs="
            + repr(self.attrs)
            + ")"
        )
        np.set_printoptions(**npopt)
        return out


class ArrayOfEncodedEqualSizedArrays(LGDO):
    """An array of encoded arrays with equal decoded size.

    Used to represent an encoded :class:`.ArrayOfEqualSizedArrays`. In addition
    to an internal :class:`.VectorOfVectors` `self.encoded_data` storing the
    encoded data, the size of the decoded arrays is stored in a
    :class:`.Scalar` `self.encoded_size`.

    See Also
    --------
    .ArrayOfEqualSizedArrays
    """

    def __init__(
        self,
        encoded_data: VectorOfVectors = None,
        decoded_size: Scalar | int = None,
        attrs: dict[str, Any] = None,
    ) -> None:
        """
        Parameters
        ----------
        encoded_data
            the vector of vectors holding the encoded data.
        decoded_size
            the length of the decoded arrays.
        attrs
            A set of user attributes to be carried along with this LGDO. Should
            include information about the codec used to encode the data.
        """
        if isinstance(encoded_data, VectorOfVectors):
            self.encoded_data = encoded_data
        elif encoded_data is None:
            self.encoded_data = VectorOfVectors(dtype="ubyte")
        else:
            raise ValueError("encoded_data must be a valid VectorOfVectors")

        if isinstance(decoded_size, Scalar):
            self.decoded_size = decoded_size
        elif decoded_size is not None:
            self.decoded_size = Scalar(int(decoded_size))
        else:
            self.decoded_size = Scalar(0)

        super().__init__(attrs)

    def datatype_name(self) -> str:
        return "array"

    def form_datatype(self) -> str:
        et = utils.get_element_type(self.encoded_data)
        return "array_of_encoded_equalsized_arrays<1,1>{" + et + "}"

    def __len__(self) -> int:
        return len(self.encoded_data)

    def __eq__(self, other: ArrayOfEncodedEqualSizedArrays) -> bool:
        if isinstance(other, ArrayOfEncodedEqualSizedArrays):
            return (
                self.encoded_data == other.encoded_data
                and self.decoded_size == other.decoded_size
                and self.attrs == other.attrs
            )

        else:
            return False

    def resize(self, new_size: int) -> None:
        """Resize array along the first axis.

        See Also
        --------
        .VectorOfVectors.resize
        """
        self.encoded_data.resize(new_size)

    def __getitem__(self, i: int) -> NDArray:
        """Return encoded array at index `i`."""
        return self.encoded_data[i]

    def __iter__(self) -> Iterator[NDArray]:
        yield from self.encoded_data

    def __str__(self) -> str:
        string = ""
        pos = 0
        for vec in self:
            vec = vec.to_numpy()
            if pos != 0:
                string += " "

            string += np.array2string(
                vec,
                prefix=" ",
                formatter={
                    "int": lambda x, vec=vec: f"0x{x:02x}"
                    if vec.dtype == np.ubyte
                    else str(x)
                },
            )

            if pos < len(self.encoded_data.cumulative_length):
                string += ",\n"

            pos += 1

        string = f"[{string}] decoded_size={self.decoded_size}"

        attrs = self.getattrs()
        if len(attrs) > 0:
            string += f" with attrs={attrs}"

        return string

    def __repr__(self) -> str:
        npopt = np.get_printoptions()
        np.set_printoptions(
            threshold=5,
            edgeitems=2,
            linewidth=100,
        )
        out = (
            "ArrayOfEncodedEqualSizedArrays(encoded_data="
            + repr(self.encoded_data)
            + ", decoded_size="
            + repr(self.decoded_size)
            + ", attrs="
            + repr(self.attrs)
            + ")"
        )
        np.set_printoptions(**npopt)
        return out
