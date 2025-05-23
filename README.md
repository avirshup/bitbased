# `bitbased`

A little python library for working with immutable big-endian
bitstrings and CIDR ranges.

To install: clone this repo, `cd` into it, then `pip install .`. Python >=3.12+ is required.


<!-- TOC -->

* [`bitbased`](#bitbased)
    * [API examples](#api-examples)
        * [`bitbased.IpV4`](#bitbasedipv4)
        * [`bitbased.CidrV4`](#bitbasedcidrv4)
        * [`bitbased.BitString`](#bitbasedbitstring)
        * [Covering CIDR algorithm (
          `bitbased.covering_set`)](#covering-cidr-algorithm-bitbasedcovering_set)

<!-- TOC -->

## API examples

See also the [tests](tests/) for examples over the complete API.

### `bitbased.IpV4`

[source](bitbased/ipv4.py), [tests](tests/test_cidr_ranges.py)

The `IpV4` class is a newtype wrapper around 32-bit [`BitString`s](bitbased/bits.py).

```python
from bitbased import BitString, IpV4

my_ip = IpV4.parse("255.0.0.00")
assert my_ip == IpV4(BitString(255 << 24, length=32))

print(repr(my_ip))  # "<IpV4: 255.0.0.0 / 11111111000000000000000000000000>"
print(repr(my_ip.bits))  # "<BitString: 11111111000000000000000000000000 (4278190080)>"

print(my_ip)  # "255.0.0.0"
print(my_ip.next())  # "255.0.0.1"
print(my_ip.prev())  # "254.255.255.255"
```

### `bitbased.CidrV4`

[source](bitbased/cidrv4.py), [tests](tests/test_cidr_ranges.py)

Represents a IPv4 CIDR range.

```python
from bitbased import CidrV4, IpV4

cidr = CidrV4.parse('192.128.0.0/7')
print(cidr.human_readable_range)  # "192.128.0.[0-127]"
print(cidr.prefix)
print(cidr.usable_addresses)  # "126"

assert cidr.net_address() == IpV4.parse('192.128.0.0')  # first address
assert cidr.broadcast_address() == IpV4.parse("192.128.0.127")  # last address

print([
    str(ipaddr) for ipaddr in CidrV4.parse('1.2.3.4/2')
])  # "['1.2.3.4', '1.2.3.5', '1.2.3.6', '1.2.3.7']"
```

### `bitbased.BitString`

[source](bitbased/bitstring.py), [tests](tests/test_bit_strings.py)

Immutable bitstrings of fixed length, intrepreted as big endian values.

```python
from bitbased import BitString

# or `from bitbased import Bs` for less typing

# --- 6 ways to construct the 1-byte bitstring "01010101" ---
# 0) by parsing an '0b' prefixed bin string;
b0 = BitString.parse('0b01010101')
# 1) by parsing a string of 1s and 0s (underscores are ignored);
b1 = BitString.parse('0101_0101')
# 2) by parsing an '0x' prefixed hex string;
b2 = BitString.parse('0x55')
# 3) by directly initializing the big-endian value and string length
b3 = BitString(value=85, length=8)
# 4) same as 3, but with positional args
b4 = BitString(85, 8)
# 5) by concatenating 2 bitstrings
b5 = BitString(5, 4).concat(BitString(5, 4))  # concat 0101 with 0101
assert b0 == b1 == b2 == b3 == b4 == b5

# String representations
print(repr(b0))  # "<BitString: 01010101 (85)>"
print(b0)  # "01010101"
print(b0.to_hex())  # 55

# Both bitwise operators and array indexing are available:
print(~b0)  # "10101010" 
print(b0[-1])  # "1"
print(repr(b0[:4]))  # "<BitString: 0101 (5)>"

# Note BitStrings compare equal IFF both value *and* length match
assert BitString.parse('0001') == BitString.parse('0001')
assert BitString.parse('0001') != BitString.parse('01')
```

### Covering CIDR algorithm (`bitbased.covering_set`)

[source](bitbased/covering_set.py), [tests](tests/test_covering_set.py)

Algorithm that returns the minimal contiguous set of CIDR ranges required to cover all IP addresses
between and including `ip1` and `ip2`.

Signature: `covering_set(ip1: IpV4, ip2: IpV4) -> list[CidrV4]`

```python
from bitbased import CidrV4, covering_set
from bitbased.ipv4 import IpV4

assert covering_set(
        IpV4.parse("1.1.1.0"),
        IpV4.parse("1.1.2.255"),
) == [CidrV4.parse('1.1.1.0/8'), CidrV4.parse("1.1.2.0/8")]
```
