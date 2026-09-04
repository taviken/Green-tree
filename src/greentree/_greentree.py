"""
This Module contains data structures and algorithms written in pure python that
implement a generic tree-node.
"""

from collections import deque
from typing import Union, IO, Deque, Generator, Mapping, Sequence, Any
from io import StringIO
from pprint import pprint


class NodeIndexRangeError(IndexError):
    """
    Node index range error. Subclass of IndexError.
    """
    def __init__(self, key, length):
        msg = f"Children index out of range. Valid range is {-length} to {length-1}.\
              Received key of {key}"
        super().__init__(msg)


class NodeIndexError(ValueError):
    """
    Node index error. Subclass of ValueError.
    """
    def __init__(self, value):
        msg = f"Value, {value}, not found"
        super().__init__(msg)


class NodeChildrenView(Sequence):
    """
    A read-only realtime view of Node children
    """

    def __init__(self, registry) -> None:
        self._registry = registry

    def __len__(self) -> int:
        return len(self._registry)

    def __getitem__(self, index):
        return self._registry[index]

    def __iter__(self) -> Generator[Any, Any, None]:
        yield from self._registry

    def __repr__(self):
        temp = ", ".join([f"{i} : {child!r}" for i, child in enumerate(self._registry)])
        return f"{type(self).__name__}({temp})"


def _to_dict(node: "Node") -> dict:
    """
    module helper function to convert a Node to a dict data structure
    """
    d = {"value": node.value, "tag": node.tag}
    if node.children:
        d["children"] = [_to_dict(child) for child in node.children]
    return d


def _format_tree_with_pipes(node: "Node", stream: IO, prefix="", is_last=True):
    """
    module helper function that builds a string representation of a given Node.
    """
    # Connector for the current node
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{node.value}", file=stream)

    # Prepare prefix for children
    new_prefix = prefix + ("    " if is_last else "│   ")

    # Iterate through children and recurse
    temp = list(reversed(node.children))
    while temp:
        child = temp.pop()
        _format_tree_with_pipes(child, stream, new_prefix, not bool(temp))


class Node:
    """
    This class represents a generic tree-node data structure.
    """

    __slots__ = ("value", "tag", "parent", "_children", "__weakref__")

    def __init__(self, value: object, tag: Union[str, int, None] = None):
        """
        Initiailizes the Node data structure

        Arguments:
        value -- any valid python object
        tag -- optional string tag to help identify this node. Defaults to 'None'
        """
        self.value = value
        self.tag = tag
        self.parent: "Node" | None = None
        self._children: Deque = deque()

    @property
    def children(self) -> NodeChildrenView:
        """
        This node instances children
        """
        return NodeChildrenView(self._children)

    @property
    def is_leaf(self) -> bool:
        """
        Boolean property, returns True if this is the last node in a tree.
        """
        return not self._children

    @property
    def is_binary(self) -> bool:
        """
        Boolean property, returns True if this node has exactly 2 children.
        """
        return len(self._children) == 2

    @property
    def is_root(self) -> bool:
        """
        Boolean property, returns True if this is teh top most node.
        """
        return self.parent is None

    @property
    def is_single_link(self) -> bool:
        """
        Boolean property, returns True if this node has exactly 1 child.
        """
        return len(self._children) == 1

    @property
    def as_dict(self) -> dict:
        """
        This property returns a dict representation of the tree-node.
        """
        return _to_dict(self)

    def insert_child(self, index: int, value: Union[object, "Node"]) -> None:
        """
        Inserts any valid object into the given index. If the given index exceeds
        the current length or is less than 0, it will append the child to the right(same
        as using the `add_right` method) or prepend the child to the left(same as
        using the `add_left` method) respectively.
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)
        self._children.insert(index, value)

    def add_left(self, item: Union[object, "Node"]) -> None:
        """
        This method adds an object or other node instance to the left most side.
        """
        if not isinstance(item, self.__class__):
            item = self.__class__(item)

        item.parent = self
        self._children.appendleft(item)

    def add_right(self, item: Union[object, "Node"]) -> None:
        """
        This method adds an object or other node instance to the right most side.
        """
        if not isinstance(item, self.__class__):
            item = self.__class__(item)
        item.parent = self
        self._children.append(item)

    def level_order_traversal(self, root=None) -> Generator["Node", None, None]:
        """
        Generator method. Depth first traversal algorithm.
        """
        if root is None:
            root = self
        queue = deque([root])
        while queue:
            node = queue.popleft()

            yield node

            if node._children:  # pylint: disable=protected-access
                queue.extend(node._children)  # pylint: disable=protected-access

    def pre_order_traversal(self, root=None) -> Generator["Node", None, None]:
        """
        Generator method. Breadth first traversal algorithm. Yields value first,
        continues traversal.
        """
        if root is None:
            root = self
        return self._dfs_traversal(root, True)

    def post_order_traversal(self, root=None) -> Generator["Node", None, None]:
        """
        Generator method. Breadth first traversal algorithm. Yields value last after
        finishing traversal.
        """
        if root is None:
            root = self
        return self._dfs_traversal(root, False)

    def _dfs_traversal(self, root, is_preorder=True) -> Generator["Node", None, None]:
        """
        Helper method of the bfs search algorithms, pre and post order traversal.
        """

        if is_preorder:
            yield root

        if root.children:
            for child in root.children:
                yield from self._dfs_traversal(child, is_preorder)

        if not is_preorder:
            yield root

    def __eq__(self, other: Union["Node", object]) -> bool:
        if issubclass(other.__class__, self.__class__):
            return self.value == other.value  # type: ignore[attr-defined]

        return self.value == other

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __format__(self, format_spec) -> str:
        stream = StringIO()
        if format_spec == "pipe":
            _format_tree_with_pipes(self, stream)
        elif format_spec == "dict":
            pprint(self.as_dict, stream)

        return stream.getvalue()

    def __getattr__(self, name: str):

        for child in self._children:
            if str(child.value) == name:
                return child

        # Raise standard AttributeError if child is not found
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Normalize negative bounds, omissions, and steps
            start, stop, step = key.indices(len(self._children))

            # Use a list comprehension to handle complex slicing (like negative steps)
            retval = [self._children[i] for i in range(start, stop, step)]
        else:
            try:
                retval = self._children[key]
            except IndexError as e:
                raise NodeIndexRangeError(key, len(self._children)) from e

        return retval

    def __delitem__(self, key):
        if isinstance(key, slice):
            # Convert to list to easily perform the slice deletion
            temp_list = list(self._children)
            del temp_list[key]
            # Replace the old deque content with the updated list
            self._children = deque(temp_list)
        else:
            # Handle regular single index deletion
            del self._children[key]

    def index(self, value) -> int:
        """
        This method returns the index from a given value in this Node instance. It
        raises `NodeIndexError` if no value is found.
        """
        temp = [child.value for child in self._children]
        try:
            return temp.index(value)
        except ValueError as e:
            raise NodeIndexError(value) from e

    def show(self) -> None:
        """
        Shortcut method to getting the pipe represntation of this tree-node.
        Running `print( format(<this>, 'pipe') ) yields the same result.
        """
        print(f"{self:pipe}")

    def _from_dict_recur(self, node: "Node", datadict: Mapping, node_class: type):
        """
        Helper method to recursively create a tree-node from a given mapping.
        """
        for value, children in datadict.items():
            new_node = node_class(value=value)
            node.add_right(new_node)
            if isinstance(children, Mapping):
                self._from_dict_recur(new_node, children, node_class)
            elif isinstance(children, Sequence) and not isinstance(
                children, (str, bytes)
            ):
                for child in children:
                    new_node.add_right(child)
            else:
                new_node.add_right(children)

    @classmethod
    def from_dict(cls, data: Mapping, root_name: str | None = None) -> "Node":
        """
        Classmethod. Creates a tree-node instance from a given mapping.
        """
        root_name = root_name if root_name is not None else "root"
        root = cls(value=root_name, tag=root_name)
        root._from_dict_recur(root, data, cls)
        return root


__all__ = [
    "Node",
    "NodeIndexError",
    "NodeIndexRangeError",
]
