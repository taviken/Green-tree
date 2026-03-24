Repository of python package greentree

The Green Tree package implements a pure python Node tree data structure.


Example
-------

Basic Usage:

.. code-block:: python

    from greentree import Node


    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    f = Node("f")
    g = Node("g")

    a.add_left(b)
    a.add_right(c)
    b.add_right(d)
    b.add_right(e)
    c.add_left(f)
    c.add_right(g)

Using the show method:

.. code-block:: python

    >>> a.show()
    └── a
        ├── b
        │   ├── d
        │   └── e
        └── c
            ├── f
            └── g

Using the search by tag methos:

.. code-block:: python
>>> a.search_by_tag('tag name here')




License
-------

Licensed under the `MIT License`_.

.. _MIT License: https://github.com/taviken/strictabc/blob/main/LICENSE
