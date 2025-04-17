import typing as t

import pytest

from bitbased import BitString


def test_empty():
    null = BitString(0)
    assert len(null) == 0
    assert list(null) == []
    assert str(null) == ""


def test_zero():
    zero = BitString(0, 3)
    assert len(zero) == 3
    assert tuple(zero) == (0, 0, 0)
    assert str(zero) == "000"


def test_one():
    one = BitString(1)
    assert one.value == 1
    assert one.length == 1
    assert list(one) == [1]
    assert str(one) == "1"


def test_padded_one():
    one = BitString(1, length=2)

    assert one.value == 1
    assert one.length == 2
    assert str(one) == "01"

    assert list(one) == [0, 1]
    assert one[0] == 0
    assert one[1] == 1
    assert one[-1] == 1
    assert one[-2] == 0

    for bad_idx in (-10, -3, 2, 10):
        with pytest.raises(IndexError):
            _ = one[bad_idx]


def test_constructors():
    padone = BitString(1, length=2)
    assert BitString.from_bits((0, 1)) == padone
    assert BitString.parse("01") == padone
    assert BitString.parse("0b01") == padone
    assert BitString.parse("0x1") == BitString(1, length=4)

    assert BitString.parse("0x01") == BitString(1, length=8)
    assert BitString.ones(5) == BitString(0b11111, 5)
    assert BitString.zeroes(7) == BitString(0, 7)


def test_paddings():
    justone = BitString.ones(1)
    assert str(justone.pad_left(3)) == "0001"
    assert str(justone.pad_left_to_alignment(8)) == "00000001"

    assert str(justone.pad_right(2)) == "100"
    assert str(justone.pad_right_to_aligment(6)) == "100000"


def test_bitwise_ops():
    b1 = BitString.parse("000111")
    b2 = BitString.parse("111000")

    assert b1 << 3 == BitString.parse("000111000")
    assert b2 >> 3 == BitString.ones(3)
    assert b1 & b2 == BitString.zeroes(6)
    assert b1 | b2 == BitString.ones(6)
    assert b1 ^ b2 == BitString.ones(6)
    assert ~b1 == b2


def test_mutations():
    assert str(BitString.ones(3).concat(BitString.zeroes(5))) == "11100000"
    assert ~BitString.ones(5) == BitString.zeroes(5)
    assert ~~BitString.zeroes(13) == BitString(0, 13)

    twelve = BitString.parse("00001100")
    assert twelve.value == 12  # sanity check
    assert twelve.set_bit(0, 1) == BitString(128 + 12, length=8)

    assert twelve.flip_bit(-1).value == 13
    assert twelve.set_bit(7, 1).value == 13

    assert twelve.flip_bit(-3).value == 8
    assert twelve.set_bit(5, 0).value == 8


def test_iter_chunks():
    mystring = BitString.parse("0011" * 8)
    assert list(mystring.iter_bytes()) == [BitString.parse("00110011")] * 4
