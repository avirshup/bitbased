import typing as t
from .util import group_digits

from .bits import BitString

__all__ = [
    "hex_table",
    "print_hex_table",
    "aligned_bit_table",
    "print_aligned_bit_table",
]

type Endian = t.Literal["big", "little"]


def hex_table(
    bs: BitString,
    bytes_per_row: int = 8,
    endian: Endian = "big",
) -> t.Iterator[str]:
    """Yield lines of an ASCII hex table for these bits.

    First line will be column labels.
    Automatically pads with 0s to the nearest byte if necessary.
    Yields in big endian order by default, pass `endian='little'` to get
    least significant bytes first.
    """

    # header
    yield " ".join((" ___|", *(f"{i:2x}" for i in range(bytes_per_row))))

    def _fmt_row(row: int, cells: list[str]) -> str:
        return f'{row:>3x} | {" ".join(cells)}'

    byte_iter = bs.iter_bytes(autopad=True)
    if endian == "little":
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
    endian: Endian = "big",
    file: t.TextIO | None = None,
):
    """convenience"""
    for line in hex_table(bs, bytes_per_row=bytes_per_row, endian=endian):
        print(line, file=file)


def aligned_bit_table(*bitstrings: BitString, sep: str = "_") -> t.Iterator[str]:
    """Print bit strings all right-aligned with each other in a table"""

    if len(sep) != 1:
        raise ValueError(f"Delimiter must be a single character, but got: '{sep}'")

    # figure out length
    max_len = max(bs.length for bs in bitstrings)
    maxquads, rem = divmod(max_len, 4)
    if rem:
        maxquads += 1

    # header
    yield "".join(f"{4*n:>4}↓" for n in reversed(range(maxquads)))

    # print each bitstring, all in a row
    for bs in bitstrings:
        s = "".join(group_digits(str(bs), 4, sep=sep))
        yield f"{s:>{maxquads * 5}}"


def print_aligned_bit_table(
    *bitstrings: BitString, file: t.TextIO | None = None
) -> t.Iterator[str]:
    """convenience"""
    for line in aligned_bit_table(*bitstrings):
        print(line, file=file)
