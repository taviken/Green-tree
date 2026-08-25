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
    assert str(view) == "ChildrenView([Node('b'), Node('c')])"


def test_dir(setup1):
    a, *_ = setup1
    assert dir(a) == [
        "__class__",
        "__delattr__",
        "__dir__",
        "__doc__",
        "__eq__",
        "__firstlineno__",
        "__format__",
        "__ge__",
        "__getattr__",
        "__getattribute__",
        "__getstate__",
        "__gt__",
        "__hash__",
        "__init__",
        "__init_subclass__",
        "__le__",
        "__lt__",
        "__module__",
        "__ne__",
        "__new__",
        "__reduce__",
        "__reduce_ex__",
        "__repr__",
        "__setattr__",
        "__sizeof__",
        "__slots__",
        "__static_attributes__",
        "__str__",
        "__subclasshook__",
        "_children",
        "_dfs_traversal",
        "_from_dict_recur",
        "add_left",
        "add_right",
        "as_dict",
        "b",
        "c",
        "children",
        "from_dict",
        "is_binary",
        "is_leaf",
        "is_root",
        "is_single_link",
        "level_order_traversal",
        "parent",
        "post_order_traversal",
        "pre_order_traversal",
        "show",
        "tag",
        "value",
    ]
