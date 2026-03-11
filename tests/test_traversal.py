from src.greentree import *
import pytest


@pytest.fixture
def setup1():
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    f = Node("f")
    g = Node("g")

    a.add_right(b)
    a.add_right(c)
    b.add_right(d)
    b.add_right(e)
    c.add_right(f)
    c.add_right(g)
    return a, b, c, d, e, f, g


@pytest.fixture
def setup2():
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d1 = Node("d")
    d2 = Node("d")
    a.add_right(b)
    a.add_right(c)
    b.add_right(d1)
    c.add_right(d2)
    return a, b, c, d1, d2


def test_level_order(setup1):
    a, b, c, d, e, f, g = setup1
    assert tuple(a.level_order_traversal()) == (a, b, c, d, e, f, g)


def test_pre_order(setup1):
    a, b, c, d, e, f, g = setup1
    assert tuple(a.pre_order_traversal()) == (a, b, d, e, c, f, g)


def test_post_order(setup1):
    a, b, c, d, e, f, g = setup1
    assert tuple(a.post_order_traversal()) == (d, e, b, f, g, c, a)
