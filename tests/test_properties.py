from src.greentree import *
import pytest
from io import StringIO
from contextlib import redirect_stdout


@pytest.fixture
def setup1():
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    g = Node("g")

    a.add_left(b)
    a.add_right(c)
    b.add_right(d)
    b.add_right(e)
    c.add_left("f")
    c.add_right(g)

    f = c._children[0]
    return a, b, c, d, e, f, g


def test_eq():
    a = Node("d")
    b = Node("d")
    assert a == b
    assert a == "d"
    assert "d" == a
    assert a is not b


def test_tree_prop(setup1):
    a, b, c, _, e, _, g = setup1
    g.add_right("h")
    assert a.is_root
    assert not b.is_root
    assert c.is_binary
    assert e.is_leaf
    assert g.is_single_link


def test_repr():
    a = Node("a")
    assert eval(repr(a)) == a


def test_as_dict(setup1):
    a, *_ = setup1
    assert a.as_dict == {
        "value": "a",
        "tag": None,
        "children": [
            {
                "value": "b",
                "tag": None,
                "children": [{"value": "d", "tag": None}, {"value": "e", "tag": None}],
            },
            {
                "value": "c",
                "tag": None,
                "children": [{"value": "f", "tag": None}, {"value": "g", "tag": None}],
            },
        ],
    }


def test_format(setup1):
    a, *_ = setup1
    assert (
        format(a, "pipe")
        == "└── a\n    ├── b\n    │   ├── d\n    │   └── e\n    └── c\n        ├── f\n        └── g\n"
    )

    assert (
        f"{a:dict}"
        == "{'children': [{'children': [{'tag': None, 'value': 'd'},\n                            {'tag': None, 'value': 'e'}],\n               'tag': None,\n               'value': 'b'},\n              {'children': [{'tag': None, 'value': 'f'},\n                            {'tag': None, 'value': 'g'}],\n               'tag': None,\n               'value': 'c'}],\n 'tag': None,\n 'value': 'a'}\n"
    )


def test_show(setup1):
    a, *_ = setup1
    stream = StringIO()
    with redirect_stdout(stream):
        a.show()
    assert (
        stream.getvalue().strip()
        == "└── a\n    ├── b\n    │   ├── d\n    │   └── e\n    └── c\n        ├── f\n        └── g"
    )


def test_from_dict():
    data = {"a": {"b": {"c": "d"}, "e": {"f": "g"}}}
    root = Node.from_dict(data)
    assert (
        format(root, "pipe")
        == "└── root\n    └── a\n        ├── b\n        │   └── c\n        │       └── d\n        └── e\n            └── f\n                └── g\n"
    )

    data["a"]["b"]["c"] = [1, 2, 3]
    root = Node.from_dict(data)
    assert (
        format(root, "pipe")
        == "└── root\n    └── a\n        ├── b\n        │   └── c\n        │       ├── 1\n        │       ├── 2\n        │       └── 3\n        └── e\n            └── f\n                └── g\n"
    )


def test_getattr(setup1):
    a, b, *_ = setup1
    assert a.b == b

    with pytest.raises(AttributeError) as e:
        a.foo


def test_children_view(setup1):
    a, *_ = setup1
    view = a.children
    assert str(view) == "NodeChildrenView(0 : Node('b'), 1 : Node('c'))"


def test_getitem():
    root = Node("root")
    for x in "defgh":
        root.add_right(x)

    a = Node("a")
    b = Node("b")
    c = Node("c")
    root.add_left(c)
    root.add_left(b)
    root.add_left(a)

    assert root[0] == a
    assert root[0:3] == [a, b, c]
    assert root[-6] == c


def test_delitem():
    root = Node("root")
    for x in "abcdefgh":
        root.add_right(x)
    del root[1:4:2]
    assert (
        format(root, "pipe")
        == "└── root\n    ├── a\n    ├── c\n    ├── e\n    ├── f\n    ├── g\n    └── h\n"
    )


def test_insert():
    root = Node("root")
    for x in "abcdefgh":
        root.add_right(x)
    root.insert_child(3, "foo")
    assert (
        format(root, "pipe")
        == "└── root\n    ├── a\n    ├── b\n    ├── c\n    ├── foo\n    ├── d\n    ├── e\n    ├── f\n    ├── g\n    └── h\n"
    )
    root.insert_child(-42, "bar")
    assert (
        format(root, "pipe")
        == "└── root\n    ├── bar\n    ├── a\n    ├── b\n    ├── c\n    ├── foo\n    ├── d\n    ├── e\n    ├── f\n    ├── g\n    └── h\n"
    )
    root.insert_child(42, "baz")
    assert (
        format(root, "pipe")
        == "└── root\n    ├── bar\n    ├── a\n    ├── b\n    ├── c\n    ├── foo\n    ├── d\n    ├── e\n    ├── f\n    ├── g\n    ├── h\n    └── baz\n"
    )
