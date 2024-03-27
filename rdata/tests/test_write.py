"""Tests of writing and Python-to-R conversion."""

from __future__ import annotations

import io
import tempfile
from contextlib import contextmanager
from typing import Callable

import pytest

import rdata
import rdata.io

TESTDATA_PATH = rdata.TESTDATA_PATH

valid_compressions = ["none", "bzip2", "gzip", "xz"]
valid_formats = ["xdr", "ascii"]


@contextmanager
def no_error() -> Callable:
    """Context manager that does nothing but returns no_error.

    This context manager can be used like pytest.raises()
    when no error is expected.
    """
    yield no_error


def decompress_data(data: memoryview) -> bytes:
    """Decompress bytes."""
    from rdata.parser._parser import FileTypes, file_type

    filetype = file_type(data)

    if filetype is FileTypes.bzip2:
        from bz2 import decompress
    elif filetype is FileTypes.gzip:
        from gzip import decompress
    elif filetype is FileTypes.xz:
        from lzma import decompress
    else:
        return data

    return decompress(data)


fnames = sorted([fpath.name for fpath in TESTDATA_PATH.glob("*.rd?")])

@pytest.mark.parametrize("fname", fnames, ids=fnames)
def test_write(fname: str) -> None:
    """Test writing RData object to a file."""
    with (TESTDATA_PATH / fname).open("rb") as f:
        data: bytes | str
        fd: io.BytesIO | io.StringIO
        data = decompress_data(f.read())
        rds = data[:2] != b"RD"
        fmt = "ascii" if data.isascii() else "xdr"

        r_data = rdata.parser.parse_data(data, expand_altrep=False)

        if fmt == "ascii":
            fd = io.StringIO()
            data = data.decode("ascii")
            data = data.replace("\r\n", "\n")
        else:
            fd = io.BytesIO()

        try:
            rdata.io.write_file(fd, r_data, format=fmt, rds=rds)
        except NotImplementedError as e:
            pytest.xfail(str(e))

        out_data = fd.getvalue()

        assert data == out_data


@pytest.mark.parametrize("fname", fnames, ids=fnames)
def test_convert_to_r(fname: str) -> None:
    """Test converting Python data to RData object."""
    with (TESTDATA_PATH / fname).open("rb") as f:
        # Skip test files without unique R->py->R transformation
        if fname in [
            "test_encodings.rda",     # encoding not kept in Python
            "test_encodings_v3.rda",  # encoding not kept in Python
            "test_list_attrs.rda",    # attributes not kept in Python
            "test_file.rda",          # attributes not kept in Python
        ]:
            pytest.skip("ambiguous R->py->R transformation")

        data = decompress_data(f.read())
        rds = data[:2] != b"RD"

        r_data = rdata.parser.parse_data(data, expand_altrep=False)

        try:
            py_data = rdata.conversion.convert(r_data)
        except NotImplementedError as e:
            pytest.skip(str(e))

        encoding = r_data.extra.encoding
        if encoding is None:
            encoding = "CP1252" if "win" in fname else "UTF-8"

        try:
            new_r_data = rdata.conversion.convert_to_r_data(
                py_data, rds=rds, versions=r_data.versions, encoding=encoding,
                )
        except NotImplementedError as e:
            pytest.xfail(str(e))

        assert r_data == new_r_data
        assert str(r_data) == str(new_r_data)


@pytest.mark.parametrize("compression", [*valid_compressions, None, "fail"])
@pytest.mark.parametrize("fmt", [*valid_formats, None, "fail"])
@pytest.mark.parametrize("rds", [True, False])
def test_write_real_file(compression: str, fmt: str, rds: bool) -> None:  # noqa: FBT001
    """Test writing RData object to a real file with compression."""
    expectation = no_error()
    if fmt not in valid_formats:
        expectation = pytest.raises(ValueError, match="(?i)unknown format")
    if compression not in valid_compressions:
        expectation = pytest.raises(ValueError, match="(?i)unknown compression")

    py_data = "Hello"
    r_data = rdata.conversion.convert_to_r_data(py_data)
    suffix = ".rds" if rds else ".rda"
    with tempfile.NamedTemporaryFile(mode="wb", suffix=suffix) as f:
        fpath = f.name

        with expectation as status:
            rdata.io.write(fpath, r_data, format=fmt, compression=compression, rds=rds)

        if status is no_error:
            new_py_data = rdata.read_rds(fpath) if rds else rdata.read_rda(fpath)
            assert py_data == new_py_data
