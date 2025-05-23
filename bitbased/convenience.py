from .bitstring import BitString
from .cidrv4 import CidrV4
from .ipv4 import IpV4

__all__ = ["Bs", "bits", "cidr", "ip"]

Bs = BitString


def bits(maybe_bits: int | str | bytes | bytearray | BitString) -> BitString:
    """Create a BitString from compatible values"""
    if isinstance(maybe_bits, int):
        return BitString(maybe_bits)
    if isinstance(maybe_bits, str):
        return BitString.parse(maybe_bits)
    if isinstance(maybe_bits, (bytes, bytearray)):
        return BitString.from_bytes(maybe_bits)

    if not isinstance(maybe_bits, BitString):
        raise TypeError(f"Cannot create BitString from {maybe_bits.__class__}")
    return maybe_bits


def ip(ip_or_str: str | IpV4) -> IpV4:
    """Ensures you've got an IpV4 object"""
    if isinstance(ip_or_str, str):
        return IpV4.parse(ip_or_str)

    if not isinstance(ip_or_str, IpV4):
        raise TypeError(f"Cannot create IpV4 from {ip_or_str.__class__}")
    return ip_or_str


def cidr(cidr_or_str: str | CidrV4) -> CidrV4:
    """Ensures you've got a CidrV4 object"""
    if isinstance(cidr_or_str, str):
        return CidrV4.parse(cidr_or_str)

    if not isinstance(cidr_or_str, CidrV4):
        raise TypeError(f"Cannot create CidrV4 from {cidr_or_str.__class__}")
    return cidr_or_str
