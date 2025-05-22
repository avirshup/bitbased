import attrs

from . import CidrV4, IpV4

__all__ = ["covering_set"]


def covering_set(ip1: IpV4, ip2: IpV4) -> list[CidrV4]:
    """minimal contiguous set of CIDRs that contains ip1 and ip2"""
    if ip1 == ip2:
        return [CidrV4(prefix=ip1.bits)]

    start, end = (ip1, ip2) if ip1 < ip2 else (ip2, ip1)

    result = []
    cidr = CidrV4(prefix=start.bits)  # start with a 32-bit prefix

    while True:
        if end in cidr:  # i.e., we're done
            assert cidr.broadcast_address() == end
            result.append(cidr)
            break
        elif cidr.prefix[-1] != 0:
            # can't expand this CIDR anymore, save it and move on
            result.append(cidr)
            cidr = CidrV4(prefix=cidr.broadcast_address().next().bits)
        else:
            # can we embiggen this range without going over?
            trial_cidr = attrs.evolve(cidr, prefix=cidr.prefix[:-1])
            if end < trial_cidr.broadcast_address():
                # reject the embiggening, save, and move on
                result.append(cidr)
                cidr = CidrV4(prefix=cidr.broadcast_address().next().bits)
            else:
                # accept the embiggening
                cidr = trial_cidr

    return result
