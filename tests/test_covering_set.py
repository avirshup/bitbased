import typing as t

import attrs
import pytest

from bitbased import CidrV4, IpV4, covering_set


@attrs.frozen
class CoverSetTestCase:
    start: str
    end: str
    expected: list[str] | None = None


@pytest.mark.parametrize(
    "case",
    (
        CoverSetTestCase(
            start="1.1.1.1",
            end="1.1.1.1",
            expected=["1.1.1.1/0"],
        ),
        CoverSetTestCase(
            start="1.1.1.0",
            end="1.1.1.255",
            expected=["1.1.1.0/8"],
        ),
        CoverSetTestCase(
            start="1.1.0.0",
            end="1.1.1.255",
            expected=["1.1.0.0/9"],
        ),
        CoverSetTestCase(
            start="1.1.1.0",
            end="1.1.2.255",
            expected=["1.1.1.0/8", "1.1.2.0/8"],
        ),
        CoverSetTestCase(
            start="1.1.0.254",
            end="1.1.3.1",
            expected=["1.1.0.254/1", "1.1.1.0/8", "1.1.2.0/8", "1.1.3.0/1"],
        ),
    ),
    ids=lambda case: f"{case.start}-{case.end}",
)
def test_covering_set(case: CoverSetTestCase):
    """Property-based validation of covering set results"""
    start = IpV4.parse(case.start)
    end = IpV4.parse(case.end)

    result = covering_set(start, end)

    # ensure CIDRs are contiguous
    assert result[0].net_address() == start
    for i in range(1, len(result)):
        assert result[i - 1].broadcast_address().next() == result[i].net_address()
    assert result[-1].broadcast_address() == end

    # input order should not matter
    assert covering_set(end, start) == result

    # check expected results if provided
    if case.expected is not None:
        expected = [CidrV4.parse(e) for e in case.expected]
        assert result == expected
