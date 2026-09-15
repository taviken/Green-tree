"""
This Module contains data structures and algorithms written in pure python that
implement a generic tree-node.
"""

from collections import deque
from typing import Union, IO, Deque, Generator, Sequence, Optional, Dict
from io import StringIO
from pprint import pprint
import sys
import json


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

    def __iter__(self):
        yield from self._registry

    def __repr__(self):
        temp = ", ".join([f"{i} : {child!r}" for i, child in enumerate(self._registry)])
        return f"{type(self).__name__}({temp})"


def _to_dict(node: "Node") -> Union[list, None]:
    """
    Module helper function to convert a Node into a mapping structural list.
    If a node has children, it returns a list of dictionaries representing its children.
    If it has no children, it returns None.
    """
    if not node.children:
        return None

    # Maintain a list of child dictionaries to natively support identical values
    return [{child.value: _to_dict(child)} for child in node.children]


def _format_tree_with_pipes(node: "Node", stream: IO, prefix="", is_last=True):
    """
    module helper function that builds a string representation of a given Node.
    """
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{node.value}", file=stream)

    new_prefix = prefix + ("    " if is_last else "│   ")

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
        Initializes the Node data structure

        Arguments:
        value -- any valid python object
        tag -- optional string tag to help identify this node. Defaults to 'None'
        """
        self.value = value
        self.tag = tag
        self.parent = None
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
        Boolean property, returns True if this is the top most node.
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
        Output Format: { self.value: { child_value: sub_mapping_or_None } }
        """
        return {self.value: _to_dict(self)}

    def insert_child(self, index: int, value: Union[object, "Node"]) -> None:
        """
        Inserts any valid object into the given index. If the given index exceeds
        the current length or is less than 0, it will append the child to the right
        or prepend the child to the left respectively.
        """
        if not isinstance(value, self.__class__):
            value = self.__class__(value)

        value.parent = self
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
        Generator method. Breadth-first traversal (BFS) algorithm.
        """
        if root is None:
            root = self
        queue = deque([root])
        while queue:
            node = queue.popleft()
            yield node
            if node._children:
                queue.extend(node._children)

    def pre_order_traversal(self, root=None) -> Generator["Node", None, None]:
        """
        Generator method. Depth-first traversal (DFS) algorithm. Yields value first,
        continues traversal.
        """
        if root is None:
            root = self
        return self._dfs_traversal(root, True)

    def post_order_traversal(self, root=None) -> Generator["Node", None, None]:
        """
        Generator method. Depth-first traversal (DFS) algorithm. Yields value last after
        finishing traversal.
        """
        if root is None:
            root = self
        return self._dfs_traversal(root, False)

    def _dfs_traversal(self, root, is_preorder=True) -> Generator["Node", None, None]:
        """
        Helper method for the depth-first search (DFS) algorithms.
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
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self._children))
            retval = [self._children[i] for i in range(start, stop, step)]
        else:
            try:
                retval = self._children[key]
            except IndexError as e:
                raise NodeIndexError(key, len(self._children)) from e
        return retval

    def __delitem__(self, key):
        if isinstance(key, slice):
            temp_list = list(self._children)
            del temp_list[key]
            self._children = deque(temp_list)
        else:
            try:
                # Resolve potential negative index checking safely before deleting
                actual_len = len(self._children)
                if key < -actual_len or key >= actual_len:
                    raise NodeIndexError(key, actual_len)

                # Delete the item via conversion or rotating the deque
                temp_list = list(self._children)
                del temp_list[key]
                self._children = deque(temp_list)
            except TypeError as e:
                raise TypeError(
                    f"Indices must be integers or slices, not {type(key).__name__}"
                ) from e

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """
        Constructs a new Node tree structure from a dictionary matching
        the format produced by the `as_dict` property.

        Expected Format: { "value": [ {"child_value": ...}, {"child_value": ...} ] }
                         or { "value": None }
        """
        if not isinstance(data, dict) or len(data) != 1:
            raise ValueError(
                "Input data must be a dictionary with exactly one root key."
            )

        root_value, children_data = next(iter(data.items()))
        root_node = cls(value=root_value)

        if children_data is not None:
            if not isinstance(children_data, list):
                raise ValueError(
                    f"Expected a list of child mappings or None, got {type(children_data).__name__}"
                )

            for child_item in children_data:
                # Reconstruct the child node and link the parent
                child_node = cls.from_dict(child_item)
                root_node.add_right(child_node)

        return root_node

    def show(self, stream=sys.stdout) -> None:
        """
        Prints a clean visual directory tree structure of this node
        and its descendants to the console.
        """
        _format_tree_with_pipes(self, stream)

    def to_json(self, stream: Optional[IO] = None, indent: int = 4) -> Union[str, None]:
        """
        Serializes the tree into a JSON format string.

        Arguments:
        stream -- A writeable file-like text stream object. Defaults to sys.stdout.
                If explicitly set to None, the method returns the serialized JSON string.
        indent -- Number of spaces used for formatting layout indentation. Default is 4.
        """

        # Calculate target stream destination
        if stream is None:
            # If the user explicitly sets stream=None, return string format
            return json.dumps(self.as_dict, indent=indent)

        # Standard processing defaulting to sys.stdout stream pipelines
        json.dump(self.as_dict, stream, indent=indent)
        return None

    @classmethod
    def from_json(cls, source: Union[str, IO]) -> "Node":
        """
        Constructs a new Node tree structure from a JSON string or an open file stream.

        Arguments:
        source -- A JSON-formatted string or a read() supporting file-like stream object.
        """
        # Check if the source is a file-like stream object or raw string data
        if isinstance(source, IO):
            data = json.load(source)
        elif isinstance(source, str):
            data = json.loads(source)
        else:
            raise TypeError(
                "Source must be a valid JSON string or a readable file-like stream object."
            )

        return cls.from_dict(data)

    def __getstate__(self) -> dict:
        """
        Gathers the node's state for pickling.
        Maps slot attributes into a dictionary.
        """
        # Read the values of the slots explicitly
        return {
            "value": self.value,
            "tag": self.tag,
            "parent": self.parent,
            # Convert the deque to a standard list so it pickling is uniform
            "_children": list(self._children),
        }

    def __setstate__(self, state: dict) -> None:
        """
        Restores the node's state during unpickling.
        """
        self.value = state["value"]
        self.tag = state["tag"]
        self.parent = state["parent"]
        # Re-initialize the deque using the unpickled list data
        self._children = deque(state["_children"])
    

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

__all__ = [
    "Node",
    "NodeIndexError",
]
