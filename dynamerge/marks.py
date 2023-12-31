from __future__ import annotations
from typing import Any
from dynamerge.merge_policy import MergePolicy, MergePolicyNode
import dataclasses

TreePath = tuple[str | int, ...]


class MarkupParser:
    def __init__(self, base_dict: dict):
        self._base_dict = base_dict
        self.merge_policy_tree = None
        self.lazy_value_map: LazyMap = None
        self.lazy_value_graph: LazyGraph = None

    def parse_tree(self):
        """Parse a dict-tree structure and return result with relevant data"""
        self.merge_policy_tree = self._recursive_parse(
            ("root",), self._base_dict, MergePolicy()
        )
        return MarkupParserResult(
            self.merge_policy_tree, self.lazy_value_map, self.lazy_value_graph
        )

    def _recursive_parse(
        self, path: TreePath, value: dict | list | Any, parent_merge_policy: MergePolicy
    ):
        # NOTE: this strategy traverse this level twice: one for parsing scope
        # marks and other for recursing inside containers.
        # It is possible to do in one round, but care should be taken to not
        # mess with index values. The index passed to the recursion should be
        # the one after removing the marks).
        if isinstance(value, dict):
            mark_list = ScopeParser.parse_from_dict(value)
            result_pair = self._merge_policy_override_process(
                parent_merge_policy, mark_list, path
            )
            current_merge_policy, next_merge_policy = result_pair
            node = MergePolicyNode(path[-1], current_merge_policy)
            for k, v in value.items():
                node.add_child(
                    self._recursive_parse(path + tuple(k), v, next_merge_policy)
                )
            return node
        elif isinstance(value, list):
            mark_list = ScopeParser.parse_from_list(value)
            result_pair = self._merge_policy_override_process(
                parent_merge_policy, mark_list, path
            )
            current_merge_policy, next_merge_policy = result_pair
            node = MergePolicyNode(path[-1], current_merge_policy)
            for k, v in enumerate(value):
                self._recursive_parse(path + type(k), v, next_merge_policy)
            return node
        elif is_token_string(value):
            token_list = TokenParser.parse(value)
            process_result = TokenProcessor.process(token_list)
            merge_policy = process_result.merge_policy
            node = MergePolicyNode(path[-1], merge_policy)
            return node
        else:
            node = MergePolicyNode(path[-1], MergePolicy())
            return node

    def _merge_policy_override_process(
        self, parent_merge_policy, mark_list, path
    ) -> tuple(MergePolicy, MergePolicy):
        # will be used in this level (contain non-inheritable path-specific policy)
        current_merge_policy = MergePolicy().inherit_load(parent_merge_policy)
        current_merge_policy.load_from_path_map(path)
        current_merge_policy.load_from_mark_list(mark_list)
        # will be used as inheritance base for subsequent levels
        next_merge_policy = MergePolicy().inherit_load(parent_merge_policy)
        next_merge_policy.load_from_mark_list(mark_list)
        return current_merge_policy, next_merge_policy

    def _backtrack_merge_policies(self, path: TreePath):
        """
        When a merge=true is found after a merge=false, all ancestors which
        have merge=false must be turned into merge=true, until
        (and excluding) root.
        """


def is_token_string(value: Any):
    """
    Consider strings starting with "@" as token-strings, which will be parsed.
    """
    return isinstance(value, str) and value.startswith("@")


@dataclasses.dataclass
class MarkupParserResult:
    merge_policy_tree: Any
    lazy_value_map: LazyMap
    lazy_value_graph: LazyGraph


class LazyMap:
    """
    Represents key-value pair(path, LazyValue).
    """


# (key-path, [dep1, dep2, ...])
GraphEdge = tuple[str | int, list[str | int]]


class LazyGraph:
    """
    given paths a, b, c and dependencies:
    a < - b
    b < - c

    lazy_graph is :
    {
        a: [b],
        b: [c],
        c: []
    }
    """

    def __init__(self):
        self._graph = {}

    def add(self, path: TreePath, *dependencies: list[TreePath]):
        self._graph[path] = dependencies

    def remove(self, path: TreePath):
        del self._graph[path]

    def iterate(self):
        ...


class ScopeParser:
    """TODO provide map-based declaration of marks"""

    @staticmethod
    def parse_container(container: dict | list):
        """
        Parse dynaconf_marks from within container(dict or list).
        Return list of(mark_attr, new_value) tuples.
        """
        mark_list = []
        if isinstance(container, dict):
            mark_list += ScopeParser.parse_from_dict(container)
        elif isinstance(container, list):
            mark_list += ScopeParser.parse_from_list(container)
        return mark_list

    @staticmethod
    def parse_from_dict(dict_data: dict) -> list:
        """
        Parse and pop/mutates(when applicable) dynaconf marks from a dict and
        return list of(mark_attr, new_value) tuples.
        """
        mark_list = []
        merge = dict_data.pop("dynaconf_merge", None)
        merge_unique = dict_data.pop("dynaconf_merge_unique", None)
        if merge is not None:
            mark_list.append(("merge", merge))
        if merge_unique is not None:
            mark_list.append(("merge_unique", merge_unique))

        return mark_list

    @staticmethod
    def parse_from_list(list_data: list) -> list:
        """
        Parse and pop/mutates(when applicable) dynaconf marks from a list and
        return list of(mark_attr, new_value) tuples.
        """
        mark_list = []
        # reverse loop
        for i in range(len(list_data) - 1, 0, -1):
            if not isinstance(list_data[i], str):
                continue

            value = list_data[i].lower()
            if value in ("dynaconf_merge",):
                list_data.pop(i)
                mark_list.append(("merge", True))
            elif value in ("dynaconf_merge=false",):
                list_data.pop(i)
                mark_list.append(("merge", False))
            elif value in ("dynaconf_merge_unique",):
                list_data.pop(i)
                mark_list.append(("merge_unique", True))
            elif value.startswith("dynaconf_id_key="):
                list_data.pop(i)
                mark_list.append(("dict_id_key", value[value.find("=") + 1 :]))
            elif value in ("@empty"):
                list_data[i] = None
        return mark_list

    @staticmethod
    def pop_from_dict(dict_data: dict):
        ...


class TokenParser:
    @staticmethod
    def parse(string: str) -> list[tuple[str, str]]:
        """
        Parse tokens in form Token + Optional[argument]:
            @token_a[args_a][@token_b[args_b]] ...
        Example:
            >> > TokenParser.parses("@foo @bar spam")
            (('foo', ''), ('bar', 'spam')
        """
        token_word = []
        token_arg = []
        token_list = []
        capture_mode = "token_word"
        for i, char in enumerate(string[1:]):
            if capture_mode == "token_word":
                if char == " ":
                    capture_mode = "token_arg"
                    continue
                else:
                    token_word.append(char)
            elif capture_mode == "token_arg":
                if char == "@":
                    capture_mode = "token_word"
                    token_list.append(("".join(token_word), "".join(token_arg[:-1])))
                    token_word.clear()
                    token_arg.clear()
                else:
                    token_arg.append(char)
        token_list.append(("".join(token_word), "".join(token_arg)))
        token_word.clear()
        token_arg.clear()
        token_list = token_list
        return token_list


class TokenProcessor:
    @staticmethod
    def process(token_list: list[tuple(int, int)]) -> TokenProcessResult:
        result = TokenProcessResult()
        result.merge_policy = MergePolicy()
        return result


@dataclasses.dataclass
class TokenProcessResult:
    merge_policy: MergePolicy = None
    lazy_dependencies: GraphEdge = None
