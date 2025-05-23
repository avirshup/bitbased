import contextlib
import typing as t

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bitbased import Bs, errors
from bitbased.util import Bit


# ───── Strategies ─────────────────────────────────────────────── #
def bitseq_strat(
    min_size: int = 0,
    max_size: int | None = None,
) -> st.SearchStrategy[t.Sequence[Bit]]:
    return st.lists(
        st.sampled_from((0, 1)),
        min_size=min_size,
        max_size=max_size,
    )


def bitstring_strat() -> st.SearchStrategy[Bs]:
    return st.builds(Bs.from_bits, bitseq_strat())


# ───── Tests ──────────────────────────────────────────────────── #
@given(
    length=st.integers(),
    value=st.integers(),
)
def test_invariants_validated(length: int, value: int):
    expected = set()
    if value < 0:
        expected.add(errors.UnhandledValueError)
    if length < 0 or (value >> length) > 0:
        expected.add(errors.LengthError)

    with pytest.raises(tuple(expected)) if expected else contextlib.nullcontext():
        Bs(value=value, length=length)


@given(
    bytedata=st.binary(),
    byteorder=st.one_of(st.just("big"), st.just("little")),
)
def test_bytes_to_bits(
    bytedata: bytes,
    byteorder: t.Literal["big", "little"],
):
    # test correctness of conversion
    bs = Bs.from_bytes(bytedata, byteorder=byteorder)
    expected_int_value = int.from_bytes(bytedata, byteorder=byteorder)
    assert bs.value == expected_int_value

    # test roundtrip back to bytes
    rtbytes = bs.to_bytes(byteorder=byteorder)
    assert rtbytes == bytedata

    # test bytewise iteration
    expected_bytes = (
        list(bytedata) if byteorder == "big" else list(reversed(bytedata))
    )
    assert [b.value for b in bs.iter_bytes()] == expected_bytes


@given(seq=bitseq_strat())
def test_bit_sequences(seq: t.Sequence[Bit]):
    bs = Bs.from_bits(seq)

    # check parsing via str type
    charstring = "".join(map(str, seq))
    assert str(bs) == charstring
    assert Bs.parse(charstring) == bs
    assert Bs.parse(f"0b{charstring}") == bs

    # check parsing w/ `0b` prefix (not valid for empty string)
    expected_val = 0 if len(charstring) == 0 else int(charstring, base=2)

    assert bs.value == expected_val
    assert len(bs) == len(charstring)
    assert list(bs) == seq


@given(bs=bitstring_strat())
def test_bitseqs(bs):
    assert bs.value.bit_length() <= bs.length
