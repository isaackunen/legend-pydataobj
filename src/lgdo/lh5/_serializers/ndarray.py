from __future__ import annotations

import logging
import sys
from bisect import bisect_left

import numpy as np

from ...types import Array
from . import datatype

log = logging.getLogger(__name__)


def _h5_read_ndarray(
    name,
    h5f,
    start_row=0,
    n_rows=sys.maxsize,
    idx=None,
    use_h5idx=False,
    obj_buf=None,
    obj_buf_start=0,
    copy_read_nda=False,
):
    # read out all arrays by slicing
    if obj_buf is not None and not isinstance(obj_buf, Array):
        msg = f"obj_buf for '{name}' not an LGDO Array"
        raise ValueError(msg)
        obj_buf = None

    # compute the number of rows to read
    # we culled idx above for start_row and n_rows, now we have to apply
    # the constraint of the length of the dataset
    ds_n_rows = h5f[name].shape[0]
    if idx is not None:
        if len(idx[0]) > 0 and idx[0][-1] >= ds_n_rows:
            log.warning("idx indexed past the end of the array in the file. Culling...")
            n_rows_to_read = bisect_left(idx[0], ds_n_rows)
            idx = (idx[0][:n_rows_to_read],)
            if len(idx[0]) == 0:
                log.warning("idx empty after culling.")
        n_rows_to_read = len(idx[0])
    else:
        n_rows_to_read = ds_n_rows - start_row
    if n_rows_to_read > n_rows:
        n_rows_to_read = n_rows

    # if idx is passed, check if we can make it a slice instead (faster)
    change_idx_to_slice = False

    # prepare the selection for the read. Use idx if available
    if idx is not None:
        # check if idx is empty and convert to slice instead
        if len(idx[0]) == 0:
            source_sel = np.s_[0:0]
            change_idx_to_slice = True
        # check if idx is contiguous and increasing
        # if so, convert it to a slice instead (faster)
        elif np.all(np.diff(idx[0]) == 1):
            source_sel = np.s_[idx[0][0] : idx[0][-1] + 1]
            change_idx_to_slice = True
        else:
            source_sel = idx
    else:
        source_sel = np.s_[start_row : start_row + n_rows_to_read]

    # Now read the array
    if obj_buf is not None and n_rows_to_read > 0:
        buf_size = obj_buf_start + n_rows_to_read
        if len(obj_buf) < buf_size:
            obj_buf.resize(buf_size)
        dest_sel = np.s_[obj_buf_start:buf_size]

        # this is required to make the read of multiple files faster
        # until a better solution found.
        if change_idx_to_slice or idx is None or use_h5idx:
            h5f[name].read_direct(obj_buf.nda, source_sel, dest_sel)
        else:
            # it is faster to read the whole object and then do fancy indexing
            obj_buf.nda[dest_sel] = h5f[name][...][source_sel]

        nda = obj_buf.nda
    elif n_rows == 0:
        tmp_shape = (0,) + h5f[name].shape[1:]
        nda = np.empty(tmp_shape, h5f[name].dtype)
    elif change_idx_to_slice or idx is None or use_h5idx:
        nda = h5f[name][source_sel]
    else:
        # it is faster to read the whole object and then do fancy indexing
        nda = h5f[name][...][source_sel]

        # if reading a list of files recursively, this is given to obj_buf on
        # the first file read. obj_buf needs to be resized and therefore
        # it needs to hold the data itself (not a view of the data).
        # a view is returned by the source_sel indexing, which cannot be resized
        # by ndarray.resize().
        if copy_read_nda:
            nda = np.copy(nda)

    # Finally, set attributes and return objects
    attrs = h5f[name].attrs

    # special handling for bools
    # (c and Julia store as uint8 so cast to bool)
    if datatype.get_nested_datatype_string(attrs["datatype"]) == "bool":
        nda = nda.astype(np.bool_)

    return (nda, attrs, n_rows_to_read)
