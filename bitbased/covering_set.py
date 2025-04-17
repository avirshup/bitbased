import typing as t

import attrs

from . import CidrV4, IpV4

__all__ = ["covering_set"]


def covering_set(ip1: IpV4, ip2: IpV4) -> list[CidrV4]:
    """minimal contiguous set of CIDRs that containes ip1 and ip2"""
    if ip1 == ip2:
        return [CidrV4(prefix=ip1.bits)]

    start, end = (ip1, ip2) if ip1 < ip2 else (ip2, ip1)

    cidrs = []
    cidr = CidrV4(prefix=start.bits)

    def _next_cidr(c: CidrV4):
        nonlocal cidr
        cidrs.append(c)
        cidr = CidrV4(prefix=cidr.broadcast_address().next().bits)

    while True:
        if end in cidr:  # i.e., we're done
            assert cidr.broadcast_address() == end
            cidrs.append(cidr)
            break
        elif cidr.prefix[-1] != 0:
            # can't expand this CIDR anymore
            _next_cidr(cidr)
        else:
            # can we embiggen this range without going over?
            trial_cidr = attrs.evolve(cidr, prefix=cidr.prefix[:-1])
            if end < trial_cidr.broadcast_address():
                # reject the embiggening
                _next_cidr(cidr)
            else:
                # accept the embiggening
                cidr = trial_cidr

    return cidrs
