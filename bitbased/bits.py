import typing as t

import attrs

from .util import Bit, alignment_padding, check_idx, parse_bits

__all__ = ["BitString"]


@attrs.frozen(repr=False, order=True)
class BitString:
    """Immutable array of bits, interpreted as the big endian value
    (i.e., like a string, where the most significant part is first)
    """

    value: int
    length: int = attrs.Factory(
        lambda self: self.value.bit_length(),
        takes_self=True,
    )

    def __attrs_post_init__(self):
        if self.value < 0:
            raise NotImplementedError("Negative values not handled")

        if self.value.bit_length() > self.length:
            raise ValueError(
                f"Invalid: value {self.value} is too large for"
                f" bit length {self.length}"
            )

    # ----- Constructors ----- #
    @classmethod
    def from_bits(cls, bits: t.Iterable[Bit]) -> t.Self:
        val = 0
        length = 0  # since iterator might be empty
        for bit in bits:
            val = (val << 1) + bit
            length += 1
        return cls(val, length)

    @classmethod
    def ones(cls, length: int) -> t.Self:
        return cls((1 << length) - 1)

    @classmethod
    def zeroes(cls, length: int) -> t.Self:
        return cls(0, length)

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        match s[:2]:
            case "0b":
                return cls.from_bits(parse_bits(s[2:]))
            case "0x":
                return cls(
                    value=int(s[2:], base=16),
                    length=4 * (len(s) - 2),
                )
            case _:
                # if here, assume string made of "1"s and "0"s
                return cls.from_bits(parse_bits(s))

    # ---- String representations ---- #
    def to_string(self) -> str:
        return "".join(map(str, self))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.to_string()} ({self.value})>"

    def __len__(self):
        return self.length

    # ---- Math --- #
    # Warning:
    #   Dunder arithmetic methods (__add__ etc.) are intentionally
    #   *not* defined!
    #   Too much ambiguity about what to do in case of overflow
    #   and differing bit lengths.

    def wrapping_add(self, other: "int | BitString") -> t.Self:
        """Addition that wraps around to 0 on overflow.

        If adding BitStrings, they must identical lengths.
        """
        match other:
            case BitString(v, _):
                self._ensure_compat_length(other)
            case int(v):
                pass
            case _:
                raise NotImplementedError(type(other))
        return attrs.evolve(
            self,
            value=(self.value + v) % 2**self.length,
        )

    def __invert__(self) -> t.Self:
        return attrs.evolve(
            self,
            value=(1 << self.length) - 1 - self.value,
        )

    def __lshift__(self, n: int) -> t.Self:
        return self.pad_right(n)

    def __rshift__(self, n: int) -> t.Self:
        return self.__class__(
            value=self.value >> n,
            length=max(self.length - n, 0),
        )

    def __and__(self, other: "BitString") -> t.Self:
        self._ensure_compat_length(other)
        return self.__class__(self.value & other.value, self.length)

    def __or__(self, other: "BitString") -> t.Self:
        self._ensure_compat_length(other)
        return self.__class__(self.value | other.value, self.length)

    def __xor__(self, other: "BitString") -> t.Self:
        self._ensure_compat_length(other)
        return self.__class__(self.value ^ other.value, self.length)

    def _ensure_compat_length(self, other: "BitString"):
        if self.length != other.length:
            raise ValueError(
                "operation not defined for BitStrings of different lengths"
            )

    # ----- Bit access ----- #
    def __iter__(self) -> t.Iterator[Bit]:
        for i in range(self.length):
            yield self[i]

    def iter_chunks(self, chunk_len: int) -> t.Iterator[t.Self]:
        if self.length % chunk_len != 0:
            raise ValueError(
                f"Bit string length ({self.length}) not divisible by {chunk_len}"
            )
        for n in range(self.length // chunk_len):
            yield self[n * chunk_len : (n + 1) * chunk_len]

    @t.overload
    def __getitem__(self, item: int) -> Bit: ...

    @t.overload
    def __getitem__(self, item: slice) -> t.Self: ...

    def __getitem__(self, item: int | slice) -> Bit | t.Self:
        if isinstance(item, int):
            idx = check_idx(item, self.length)
            return (self.value >> (self.length - idx - 1)) & 1  # pyright: ignore [reportReturnType]
        elif isinstance(item, slice):  # test it
            return self.__class__.from_bits(
                self[i] for i in range(*item.indices(self.length))
            )
        else:
            raise NotImplementedError(type(item))

    def set_bit(self, idx: int, val: Bit) -> t.Self:  # test it
        if self[idx] == val:
            return self
        else:
            return self.flip_bit(idx)

    def flip_bit(self, idx: int):  # test it
        idx = check_idx(idx, self.length)
        return attrs.evolve(
            self,
            value=self.value ^ (1 << (self.length - idx - 1)),
        )

    # ---- Mutations ---- #
    def concat(self, other: t.Self) -> t.Self:
        return self.__class__(
            value=(self.value << other.length) + other.value,
            length=self.length + other.length,
        )

    def pad_left(self, n: int) -> t.Self:
        if n == 0:
            return self
        return self.__class__(
            value=self.value,
            length=self.length + n,
        )

    def pad_right(self, n: int) -> t.Self:
        if n == 0:
            return self
        return self.__class__(
            value=self.value << n,
            length=self.length + n,
        )

    def pad_left_to_alignment(self, alignment: int) -> t.Self:
        return self.pad_left(alignment_padding(self.length, alignment))

    def pad_right_to_aligment(self, alignment: int) -> t.Self:
        return self.pad_right(alignment_padding(self.length, alignment))
