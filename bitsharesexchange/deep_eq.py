def deep_eq(_v1, _v2):
    import operator
    import types

    def _deep_dict_eq(d1, d2):
        k1 = sorted(d1.keys())
        k2 = sorted(d2.keys())
        if k1 != k2:  # keys should be exactly equal
            return False
        return sum(deep_eq(d1[k], d2[k]) for k in k1) == len(k1)

    def _deep_iter_eq(l1, l2):
        if len(l1) != len(l2):
            return False
        return sum(deep_eq(v1, v2) for v1, v2 in zip(l1, l2)) == len(l1)

    op = operator.eq
    c1, c2 = (_v1, _v2)

    # guard against strings because they are also iterable
    # and will consistently cause a RuntimeError (maximum recursion limit reached)
    if isinstance(_v1, str):
        return op(c1, c2)

    if isinstance(_v1, dict):
        op = _deep_dict_eq
    else:
        try:
            c1, c2 = (list(iter(_v1)), list(iter(_v2)))
        except TypeError:
            c1, c2 = _v1, _v2
        else:
            op = _deep_iter_eq

    return op(c1, c2)
