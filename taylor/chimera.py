"""Lazy infinite tables with O(1) access, after Haskell's chimera package.

Entry n lives in bucket n.bit_length(): bucket 0 holds index 0, and bucket k
holds the indices 2^(k-1) to 2^k - 1. Buckets double in size, so finding an
entry is a bit length and two list lookups whatever the index. A bucket is only
allocated when one of its indices is first asked for, and each entry is
computed at most once, on first access, so entries may be defined in terms of
one another in any order.
"""

_MISSING = object()
_PENDING = object()


class Chimera:
    def __init__(self, f):
        self._f = f
        self._buckets = []

    def __getitem__(self, n):
        if n < 0:
            raise IndexError(f"negative index {n}")
        k = n.bit_length()
        start = 1 << k >> 1
        buckets = self._buckets
        while len(buckets) <= k:
            buckets.append(None)
        bucket = buckets[k]
        if bucket is None:
            bucket = buckets[k] = [_MISSING] * (start or 1)
        value = bucket[n - start]
        if value is _PENDING:
            raise ValueError(f"entry {n} depends on itself")
        if value is _MISSING:
            bucket[n - start] = _PENDING
            try:
                value = self._f(n)
            except BaseException:
                bucket[n - start] = _MISSING
                raise
            bucket[n - start] = value
        return value

    __call__ = __getitem__


def memoize(f):
    """f on the naturals, with each result computed at most once."""
    return Chimera(f)


def memoize_fix(step):
    """The memoised fixpoint of step(recurse, n): step computes the entry for n
    and calls recurse(m) for any other entry it needs.

    Each entry is computed once, but an entry first reached through a long
    chain of uncomputed ones is still a chain of Python calls, so asking for
    entries roughly in order keeps clear of the recursion limit.
    """
    table = Chimera(lambda n: step(table, n))
    return table
