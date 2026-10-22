# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Minimal KiCad S-expression parser/serializer.

Atoms are kept as Python str. Quoted strings are wrapped in Q so they can be
written back with quotes; everything else (symbols, numbers) stays a plain str.
"""


class Q(str):
    """A quoted string atom."""


def parse(text):
    pos = 0
    n = len(text)
    stack = [[]]
    while pos < n:
        c = text[pos]
        if c in " \t\r\n":
            pos += 1
        elif c == "(":
            stack.append([])
            pos += 1
        elif c == ")":
            node = stack.pop()
            stack[-1].append(node)
            pos += 1
        elif c == '"':
            pos += 1
            buf = []
            while text[pos] != '"':
                if text[pos] == "\\":
                    pos += 1
                    buf.append({"n": "\n", "t": "\t"}.get(text[pos], text[pos]))
                else:
                    buf.append(text[pos])
                pos += 1
            pos += 1
            stack[-1].append(Q("".join(buf)))
        else:
            start = pos
            while pos < n and text[pos] not in ' \t\r\n()"':
                pos += 1
            stack[-1].append(text[start:pos])
    assert len(stack) == 1, "unbalanced parentheses"
    return stack[0][0] if len(stack[0]) == 1 else stack[0]


def _atom(a):
    if isinstance(a, Q):
        return '"' + a.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(a, bool):
        return "yes" if a else "no"
    if isinstance(a, float):
        s = f"{a:.4f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(a)


def dump(node, indent=0):
    if not isinstance(node, list):
        return _atom(node)
    # keep short leaf lists on one line
    if all(not isinstance(x, list) for x in node):
        return "(" + " ".join(_atom(x) for x in node) + ")"
    pad = "\t" * (indent + 1)
    head = []
    rest = []
    for x in node:
        if isinstance(x, list) or rest:
            rest.append(x)
        else:
            head.append(x)
    out = "(" + " ".join(_atom(x) for x in head)
    for x in rest:
        out += "\n" + pad + dump(x, indent + 1)
    return out + "\n" + "\t" * indent + ")"


def find(node, key):
    """First direct child list whose head is key."""
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def find_all(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def walk(node, key):
    """All descendant lists (any depth) whose head is key."""
    if isinstance(node, list):
        if node and node[0] == key:
            yield node
        for x in node:
            yield from walk(x, key)
