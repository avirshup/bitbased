import typing as t

import attrs

from .util import (
    Bit,
    alignment_padding,
    check_idx,
    parse_bits,
    ReversibleMap,
    group_digits,
)

__all__ = ["BitString"]


@attrs.frozen(repr=False, order=True)
class BitString:
    """Immutable array of bits, interpreted as the big endian value
    (i.e., like a string, where the most significant part is first).
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
        assert length >= 0
        return cls((1 << length) - 1)

    @classmethod
    def zeroes(cls, length: int) -> t.Self:
        assert length >= 0
        return cls(0, length)

    @classmethod
    def parse(cls, s: str) -> t.Self:
        match s[:2]:
            case "0b":
                return cls.from_bits(parse_bits(s[2:]))
            case "0x":
                return cls(
                    value=int(s[2:], base=16),
                    length=4 * (len(s.replace("_", "")) - 2),
                )
            case _:
                # if here, assume string made of "1"s and "0"s
                return cls.from_bits(parse_bits(s))

    # ---- String representations ---- #
    def __str__(self) -> str:
        """Just gives you a string of 1s and 0s"""
        return self.to_bin()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self} ({self.value})>"

    # def __format__(self, format_spec: str) -> str:
    #     """TODO: implement this, ideally using the builtin implementation to
    #     do as much as possible (both parsing the spec and formatting stuff)
    #     See:
    #     - https://docs.python.org/3/reference/datamodel.html#object.__format__
    #     - https://docs.python.org/3/library/string.html#formatspec
    #     - https://github.com/doconix/string-format-full
    #     """
    #     raise NotImplementedError()

    def to_bin(self) -> str:
        """Just the string of 1s and 0s

        TODO: add args (e.g., digit separators) that can be used to implement format specifiers
        """
        return "".join(map(str, self))

    def to_hex(self, autopad: bool = False) -> str:
        """Return value as hex digits, including leading 0s.
        *Must* be aligned to 4 bits or pass "autopad=True".
        Does not include any `0x` prefix.

        TODO: add args (e.g., digit separators) that can be used to implement format specifiers
        """
        bs = self.pad_left_to_alignment(4) if autopad else self

        if bs.length % 4 != 0:
            assert not autopad
            raise ValueError("Must have length divisible by 4, or pass autopad=True")
        return f"{bs.value:0{bs.length // 4}x}"

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

    # ----- Iterators ----- #
    def __iter__(self) -> t.Iterator[Bit]:
        for i in range(self.length):
            yield self[i]

    def __reversed__(self) -> t.Iterator[Bit]:
        for i in reversed(range(self.length)):
            yield self[i]

    def iter_chunks(
        self,
        chunk_len: int,
        autopad: bool = False,
    ) -> t.Reversible[t.Self]:
        """Return reversible iterator over chunks.

        Args:
            chunk_len: length of chunks to yield
            autopad: automatically left-pad the highest chunk with 0s
                into alignment with `chunk_len` (default False)
        """
        if self.length % chunk_len == 0:
            bs = self
        elif autopad:
            bs = self.pad_left_to_alignment(chunk_len)
        else:
            raise ValueError(
                f"Bit string length ({self.length}) not divisible by {chunk_len}"
            )

        return ReversibleMap(
            fn=lambda idx: self[idx * chunk_len : (idx + 1) * chunk_len],
            vals=range(bs.length // chunk_len),
        )

    def iter_bytes(
        self,
        autopad: bool = False,
    ) -> t.Reversible[t.Self]:
        """Yield bytes. Equivalent to self.iter_chunks(8)"""
        return self.iter_chunks(8, autopad=autopad)

    # ───── Indexing ───────────────────────────────────────────────── #
    def __len__(self):
        return self.length

    @t.overload
    def __getitem__(self, item: int) -> Bit: ...

    @t.overload
    def __getitem__(self, item: slice) -> t.Self: ...

    def __getitem__(self, item: int | slice) -> Bit | t.Self:
        if isinstance(item, int):
            idx = check_idx(item, self.length)
            return (
                self.value >> (self.length - idx - 1)
            ) & 1  # pyright: ignore [reportReturnType]
        elif isinstance(item, slice):  # test it
            return self.__class__.from_bits(
                self[i] for i in range(*item.indices(self.length))
            )
        else:
            raise NotImplementedError(type(item))

    def set_bit(self, idx: int, val: Bit) -> t.Self:
        if self[idx] == val:
            return self
        else:
            return self.flip_bit(idx)

    def flip_bit(self, idx: int):
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
