import typing as t

import pytest

from bitbased import BitString


def test_empty():
    null = BitString(0)
    assert len(null) == 0
    assert list(null) == []
    assert null.to_string() == ""


def test_zero():
    zero = BitString(0, 3)
    assert len(zero) == 3
    assert tuple(zero) == (0, 0, 0)
    assert zero.to_string() == "000"


def test_one():
    one = BitString(1)
    assert one.value == 1
    assert one.length == 1
    assert list(one) == [1]
    assert one.to_string() == "1"


def test_padded_one():
    one = BitString(1, length=2)

    assert one.value == 1
    assert one.length == 2
    assert one.to_string() == "01"

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
    assert BitString.from_string("01") == padone
    assert BitString.from_string("0b01") == padone

    assert BitString.from_string("0x01") == BitString(1, length=8)
    assert BitString.ones(5) == BitString(0b11111, 5)
    assert BitString.zeroes(7) == BitString(0, 7)


def test_paddings():
    mybs = BitString.ones(1)
    assert mybs.pad_left(3).to_string() == "0001"
    assert mybs.pad_left_to_alignment(8).to_string() == "00000001"

    assert mybs.pad_right(2).to_string() == "100"
    assert mybs.pad_right_to_aligment(6).to_string() == "100000"


def test_mutations():
    assert BitString.ones(3).concat(BitString.zeroes(5)).to_string() == "11100000"
    assert BitString.ones(5).negate() == BitString.zeroes(5)
    assert BitString.zeroes(13).negate().negate() == BitString(0, 13)

    twelve = BitString.from_string("00001100")
    assert twelve.set_bit(0, 1) == BitString(128 + 12, length=8)

    assert twelve.flip_bit(-1).value == 13
    assert twelve.set_bit(7, 1).value == 13

    assert twelve.flip_bit(-3).value == 8
    assert twelve.set_bit(5, 0).value == 8


def test_iter_chunks():
    mystring = BitString.from_string("0011" * 8)
    assert (
        list(mystring.iter_chunks(8)) == [BitString.from_string("00110011")] * 4
    )
