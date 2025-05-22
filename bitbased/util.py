import typing as t
import attrs

__all__ = ["Bit", "alignment_padding", "check_idx", "parse_bits", "ReversibleMap"]

type Bit = t.Literal[0, 1]


def parse_bits(s: str) -> t.Iterator[Bit]:
    for c in s:
        match c:
            case "1":
                yield 1
            case "0":
                yield 0
            case "_":
                # technically these shouldn't be allowed to repeat
                continue
            case other:
                raise ValueError(f"Not 0/1: {other}")


def alignment_padding(length: int, alignment: int) -> int:
    rem = length % alignment
    if rem == 0:
        return 0
    return alignment - rem


def check_idx(input_idx: int, length: int):
    idx = input_idx if input_idx >= 0 else (length + input_idx)
    if not (0 <= idx < length):
        raise IndexError(f"index {input_idx} out of range for length {length})")
    return idx


@attrs.frozen
class ReversibleMap[In, Out](t.Reversible[Out]):
    fn: t.Callable[[In], Out]
    vals: t.Reversible[In]

    def __iter__(self) -> t.Iterator[Out]:
        for val in self.vals:
            yield self.fn(val)

    def __reversed__(self) -> t.Iterator[Out]:
        for val in reversed(self.vals):
            yield self.fn(val)


def group_digits(
    chars: t.Sequence[str],
    chunksize: int,
    sep: str = "_",
) -> t.Iterator[str]:
    """Groups digits for pretty-printing with the given separator.

    Examples:
        >>> ''.join(group_digits('9123456', 3, sep=','))
        "9,123,456"
        >>> ''.join(group_digits('ab1255ff', 2))
        "ab_12_55_ff"
    """
    offset = chunksize - len(chars) % chunksize
    for ic, char in enumerate(str(chars)):
        if ic != 0 and ((ic + offset) % chunksize == 0):
            yield sep
        yield char
