import typing as t

import attrs

from .bits import BitString

__all__ = ["CidrV4", "IpV4"]


@attrs.frozen(repr=False)
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
        return self.__class__(
            bits=attrs.evolve(
                self.bits,
                value=self.bits.value - 1,
            )
        )

    def next(self) -> t.Self:
        return self.__class__(
            bits=attrs.evolve(
                self.bits,
                value=self.bits.value + 1,
            )
        )

    @classmethod
    def parse(cls, s: str) -> t.Self:  # test it
        fields = s.split(".")
        if len(fields) != 4:
            raise ValueError(f"Cannot parse {s} as an IPv4 address")
        bs = BitString(0)
        for field in fields:
            bs = bs.concat(BitString(int(field), length=8))
        return cls(bs)


@attrs.frozen(repr=False)
class CidrV4:
    prefix: BitString
    nbits: int = attrs.field(
        init=False,
        default=attrs.Factory(
            lambda self: 32 - self.prefix.length,
            takes_self=True,
        ),
    )

    def __attrs_post_init__(self):
        if self.prefix.length > 32:
            raise ValueError(
                f"CIDR prefix must be <32 bits, got {self.prefix.length}"
            )

    def __str__(self) -> str:
        return f"{self.net_address()}/{self.nbits}"

    def __repr__(self) -> str:
        return f"<CidrV4: {self}>"

    def __contains__(self, item: IpV4) -> bool:
        return item.bits[: self.prefix.length] == self.prefix

    @classmethod
    def parse(cls, s: str) -> t.Self:
        ip_s, nbits_s = s.split("/")
        nbits = int(nbits_s)
        ip = IpV4.parse(ip_s)
        if ip.bits[-nbits:].value != 0:
            raise ValueError(f"Invalid CIDR {s}: not aligned to {nbits}-boundary")
        return cls(prefix=ip.bits[: 32 - nbits])

    def prev(self) -> t.Self:
        return self.__class__(
            prefix=attrs.evolve(
                self.prefix,
                value=self.prefix.value - 1,
            ),
        )

    def next(self) -> t.Self:
        return self.__class__(
            prefix=attrs.evolve(
                self.prefix,
                value=self.prefix.value + 1,
            ),
        )

    def iter_addresses(self) -> t.Iterator[IpV4]:
        addr = self.net_address()
        for _ in range(2**self.nbits):
            yield addr
            addr = addr.next()

    def net_address(self) -> IpV4:
        """The first address in the range"""
        return IpV4(self.prefix.pad_right(self.nbits))

    def broadcast_address(self) -> IpV4:
        """The last address in the range"""
        return IpV4(self.prefix.concat(BitString.ones(self.nbits)))

    @property
    def usable_addresses(self) -> int:
        return max(2**self.nbits - 2, 0)

    @property
    def human_readable_range(self) -> str:
        """Human-readable range

        Examples:
            >>> CidrV4.parse('128.25.16.0/12').human_readable_range
            '128.25.[16-31].[0-255]'"""

        # first, get full bytes, which are fixed octets in the IP
        n_full_octets = self.prefix.length // 8
        fields: list[str] = []
        for byte in self.prefix[: 8 * n_full_octets].iter_bytes():
            fields.append(str(byte.value))

        # calculate range if there's a partial octet range
        partial_byte = self.prefix[8 * n_full_octets :]
        if partial_byte.length > 0:
            freebits = 8 - partial_byte.length
            min_val = partial_byte.concat(BitString.zeroes(freebits)).value
            max_val = partial_byte.concat(BitString.ones(freebits)).value
            fields.append(f"[{min_val}-{max_val}]")

        # rest of the octets
        while len(fields) < 4:
            fields.append("[0-255]")

        return ".".join(fields)
