import typing as t

from bitbased import BitString, CidrV4, IpV4


def test_ipv4():
    my_ip = IpV4.parse("255.0.0.00")
    assert str(my_ip) == "255.0.0.0"

    assert my_ip.bits == BitString.parse("0xff_00_00_00")


def test_octet_aligned_cidrv4():
    cidr = CidrV4.parse("123.12.0.0/16")
    assert cidr.prefix == BitString((123 << 8) + 12, length=16)
    assert cidr.nbits == 16
    assert str(cidr.net_address()) == "123.12.0.0"
    assert str(cidr.broadcast_address()) == "123.12.255.255"
    assert cidr.human_readable_range == "123.12.[0-255].[0-255]"

    assert cidr.prev() == CidrV4.parse("123.11.0.0/16")
    assert cidr.next() == CidrV4.parse("123.13.0.0/16")
    assert cidr.usable_addresses == 2**16 - 2


def test_partial_octet_cidrv4():
    cidr = CidrV4.parse("1.14.32.0/13")
    assert cidr.human_readable_range == "1.14.[32-63].[0-255]"

    all_addresses = list(cidr.iter_addresses())
    assert all_addresses[0] == cidr.net_address()
    assert all_addresses[-1] == cidr.broadcast_address()
    assert len(all_addresses) == cidr.usable_addresses + 2


def test_set_memberships():
    cidr = CidrV4.parse("1.14.32.0/13")

    assert IpV4.parse("1.14.35.200") in cidr
    assert IpV4.parse("1.14.30.200") not in cidr

    subset = CidrV4.parse("1.14.35.0/8")
    assert subset in cidr
    assert cidr not in subset
    assert cidr in cidr
