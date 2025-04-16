import typing as t

__all__ = ["Bit", "alignment_padding", "check_idx", "parse_bits"]

type Bit = t.Literal[0, 1]


def parse_bits(s: str) -> t.Iterator[Bit]:
    for c in s:
        match c:
            case "1":
                yield 1
            case "0":
                yield 0
            case other:
                raise ValueError(f"Not 0/1: {other}")


def alignment_padding(length: int, alignment: int) -> int:
    rem = length % alignment
    if rem == 0:
        return 0
    return alignment - rem


def check_idx(input_idx: int, length: int):
    idx = input_idx if input_idx >= 0 else length + input_idx
    if not (0 <= idx < length):
        raise IndexError(f"index {input_idx} out of range for length {length})")
    return idx
