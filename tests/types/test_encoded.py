import numpy as np

from lgdo import (
    Array,
    ArrayOfEncodedEqualSizedArrays,
    Scalar,
    VectorOfEncodedVectors,
    VectorOfVectors,
)


def test_voev_init():
    voev = VectorOfEncodedVectors(
        VectorOfVectors(cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16")
    )
    assert len(voev.decoded_size) == 100
    assert voev.attrs["datatype"] == "array<1>{encoded_array<1>{real}}"
    assert len(voev) == 100

    voev = VectorOfEncodedVectors(
        encoded_data=VectorOfVectors(
            cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16"
        ),
        decoded_size=Array(shape=100),
        attrs={"sth": 1},
    )
    assert voev.attrs == {"datatype": "array<1>{encoded_array<1>{real}}", "sth": 1}


def test_aoeesa_init():
    voev = ArrayOfEncodedEqualSizedArrays(
        VectorOfVectors(cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16")
    )
    assert isinstance(voev.decoded_size, Scalar)
    assert voev.attrs["datatype"] == "array_of_encoded_equalsized_arrays<1,1>{real}"
    assert len(voev) == 100

    voev = ArrayOfEncodedEqualSizedArrays(
        encoded_data=VectorOfVectors(
            cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16"
        ),
        decoded_size=99,
        attrs={"sth": 1},
    )
    assert voev.decoded_size.value == 99
    assert voev.attrs == {
        "datatype": "array_of_encoded_equalsized_arrays<1,1>{real}",
        "sth": 1,
    }


def test_resize():
    voev = VectorOfEncodedVectors(
        encoded_data=VectorOfVectors(
            cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16"
        ),
        decoded_size=Array(shape=100),
    )
    voev.resize(50)
    assert len(voev) == 50

    voev = ArrayOfEncodedEqualSizedArrays(
        encoded_data=VectorOfVectors(
            cumulative_length=1000 * (np.arange(100) + 1), dtype="uint16"
        ),
        decoded_size=99,
    )
    voev.resize(50)
    assert len(voev) == 50


def test_voev_iteration():
    voev = VectorOfEncodedVectors(
        encoded_data=VectorOfVectors(
            flattened_data=Array(nda=np.array([1, 2, 3, 4, 5, 2, 4, 8, 9, 7, 5, 3, 1])),
            cumulative_length=Array(nda=np.array([2, 5, 6, 10, 13])),
        ),
        decoded_size=Array(shape=5, fill_val=6),
    )

    desired = [
        [1, 2],
        [3, 4, 5],
        [2],
        [4, 8, 9, 7],
        [5, 3, 1],
    ]

    for i, (v, s) in enumerate(voev):
        assert np.array_equal(v, desired[i])
        assert s == 6


def test_aoeesa_iteration():
    voev = ArrayOfEncodedEqualSizedArrays(
        encoded_data=VectorOfVectors(
            flattened_data=Array(nda=np.array([1, 2, 3, 4, 5, 2, 4, 8, 9, 7, 5, 3, 1])),
            cumulative_length=Array(nda=np.array([2, 5, 6, 10, 13])),
        ),
        decoded_size=99,
    )

    desired = [
        [1, 2],
        [3, 4, 5],
        [2],
        [4, 8, 9, 7],
        [5, 3, 1],
    ]

    for i, v in enumerate(voev):
        assert np.array_equal(v, desired[i])
