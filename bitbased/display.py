import typing as t

from .bitstring import BitString
from .util import ByteOrder, group_digits

__all__ = [
    "aligned_bit_table",
    "hex_table",
    "print_aligned_bit_table",
    "print_hex_table",
]


def hex_table(
    bs: BitString,
    bytes_per_row: int = 8,
    byteorder: ByteOrder = "big",
) -> t.Iterator[str]:
    """Yield lines of an ASCII hex table for these bits.

    First line will be column labels.
    Automatically pads with 0s to the nearest byte if necessary.
    Yields in big endian order by default, pass `endian='little'` to get
    least significant bytes first.

    See `print_hex_table` for output example.
    """

    # header
    yield " ".join((" ___|", *(f"{i:2x}" for i in range(bytes_per_row))))

    def _fmt_row(row: int, cells: list[str]) -> str:
        return f"{row:>3x} | {' '.join(cells)}"

    byte_iter = bs.iter_bytes(autopad=True)
    if byteorder == "little":
        byte_iter = reversed(byte_iter)

    nline = 0
    thisline = []
    for b in byte_iter:
        thisline.append(f"{b.value:<02x}")

        if len(thisline) == bytes_per_row:
            yield _fmt_row(nline, thisline)
            nline += 1
            thisline.clear()

    if thisline:  # partial last line
        yield _fmt_row(nline, thisline)


def print_hex_table(
    bs,
    bytes_per_row: int = 8,
    byteorder: ByteOrder = "big",
    file: t.TextIO | None = None,
):
    """Generate hex table and print to stream (stdout by default)

    Example:
        >>> from bitbased import *
        >>> print_hex_table(bits(b'some ascii text'))
         ___|  0  1  2  3  4  5  6  7
          0 | 73 6f 6d 65 20 61 73 63
          1 | 69 69 20 74 65 78 74
    """
    for line in hex_table(bs, bytes_per_row=bytes_per_row, byteorder=byteorder):
        print(line, file=file)


def aligned_bit_table(
    *bitstrings: BitString,
    sep: str = "_",
) -> t.Iterator[str]:
    """Yield lines of table showing bitstrings aligned with each other

    See `print_aligned_bit_table` for example output.
    """

    if len(sep) != 1:
        raise ValueError(
            f"Delimiter must be a single character, but got: '{sep}'"
        )

    # figure out length
    max_len = max(bs.length for bs in bitstrings)
    maxquads, rem = divmod(max_len, 4)
    if rem:
        maxquads += 1

    # header
    yield "".join(f"{4 * n:>4}↓" for n in reversed(range(maxquads)))

    # print each bitstring, all in a row
    for bs in bitstrings:
        s = "".join(group_digits(str(bs), 4, sep=sep))
        yield f"{s:>{maxquads * 5}}"


def print_aligned_bit_table(
    *bitstrings: BitString,
    sep: str = "_",
    file: t.TextIO | None = None,
):
    """Generate bit table and print to stream (stdout by default)

    Example:
        >>> from bitbased import bits
        >>> print_aligned_bit_table(bits(256), bits(255), bits('0x0ff'))
           8↓   4↓   0↓
            1_0000_0000
              1111_1111
         0000_1111_1111
    """
    for line in aligned_bit_table(*bitstrings, sep=sep):
        print(line, file=file)
