# `bitbased`

<!-- TOC -->
* [`bitbased`](#bitbased)
  * [API examples](#api-examples)
    * [`bitbased.IpV4`](#bitbasedipv4)
    * [`bitbased.CidrV4`](#bitbasedcidrv4)
    * [`bitbased.covering_set(ip1: IpV4, ip2: IpV4) -> list[CidrV4]`](#bitbasedcovering_setip1-ipv4-ip2-ipv4---listcidrv4)
    * [`bitbased.BitString`](#bitbasedbitstring)
<!-- TOC -->

A little python library for working with immutable big-endian
bitstrings and CIDR ranges.

To install: clone this repo, `cd` into it, then `pip install .`. Python >=3.12+ is required.

## API examples

See also the [tests](tests/) for examples over the complete API.

### `bitbased.IpV4`

The `IpV4` class is essentially a newtype wrapper around a 32-bit BitString.

```python
from bitbased import IpV4, BitString

my_ip = IpV4.parse("255.0.0.00")
assert my_ip == IpV4(BitString(255 << 24, length=32))

print(repr(my_ip)) # "<IpV4: 255.0.0.0 / 11111111000000000000000000000000>"
print(repr(my_ip.bits))  # "<BitString: 11111111000000000000000000000000 (4278190080)>"

print(my_ip) # "255.0.0.0"
print(my_ip.next()) # "255.0.0.1"
print(my_ip.prev()) # "254.255.255.255"
```


### `bitbased.CidrV4`

[Source module](bitbased/ip_and_cidr_v4.py), [tests](tests/test_cidr_ranges.py)

```python
from bitbased import CidrV4, IpV4

cidr = CidrV4.parse('192.128.0.0/7')
print(cidr.human_readable_range) # "192.128.0.[0-127]"
print(cidr.usable_addresses) # "126"

assert cidr.net_address() == IpV4.parse('192.128.0.0') # first address
assert cidr.broadcast_address() == IpV4.parse("192.128.0.127") # last address
```

### `bitbased.covering_set(ip1: IpV4, ip2: IpV4) -> list[CidrV4]`

[Source module](bitbased/covering_set.py), [tests](tests/test_covering_set.py)

Algorithm that returns the minimum contiguous set of CIDR ranges required to cover all IP addresses between and including `ip1` and `ip2`.

```python
from bitbased import CidrV4, IpV4, covering_set

assert covering_set(
        IpV4.parse("1.1.1.0"),
        IpV4.parse("1.1.2.255"),
) == [CidrV4.parse('1.1.1.0/8'), CidrV4.parse("1.1.2.0/8")]
```

### `bitbased.BitString`
[Source module](bitbased/bits.py), [tests](tests/test_bit_strings.py)

Immutable bitstrings of fixed length, intrepreted as big endian values.
Here are some different ways to construct the 1-byte BitString '01010101':

```python
from bitbased import BitString

b0 = BitString.parse('0b01010101') # '0b' prefix is optional
b1 = BitString.parse('0101_0101') # underscores are ignored
b2 = BitString(value=85, length=8)
b3 = BitString(85, 8)  # same as above, without kwargs
b4 = BitString(5, 4).concat(BitString(5,4)) # concat 0101 with 0101
b5 = BitString.parse('0x55')
assert b0 == b1 == b2 == b3 == b4 == b5

print(repr(b0)) # "<BitString: 01010101 (85)>"
print(b0) # "01010101"
print(~b0) # negation operator: "10101010"

# note bitstrings are not considered equal unless they have the same length
assert BitString.parse('0001') != BitString.parse('01')
```
