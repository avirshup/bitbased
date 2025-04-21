import typing as t

import attrs

from . import BitString

__all__ = ["IpV4"]


@attrs.frozen(repr=False, order=True)
class IpV4:
    bits: BitString

    def __attrs_post_init__(self):
        if self.bits.length != 32:
            raise ValueError(
                f"IPv4 address must be 32 bits, got {self.bits.length}"
            )

    def __str__(self) -> str:
        return ".".join(str(x.value) for x in self.bits.iter_bytes())

    def __repr__(self) -> str:
        return f"<IpV4: {self} / {self.bits}>"

    def prev(self) -> t.Self:
        return self.__class__(self.bits.wrapping_add(-1))

    def next(self) -> t.Self:
        return self.__class__(self.bits.wrapping_add(1))

    @classmethod
    def parse(cls, s: str) -> t.Self:  # test it
        fields = s.split(".")
        if len(fields) != 4:
            raise ValueError(f"Cannot parse {s} as an IPv4 address")
        bs = BitString(0)
        for field in fields:
            bs = bs.concat(BitString(int(field), length=8))
        return cls(bs)
