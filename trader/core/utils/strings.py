import re


def stip_dot(s):
    return s.split('.')[0]


def first_number(s):
    m = re.match('\d+|$', s)
    return m.group(0) if m else None
