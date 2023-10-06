"""
Merge Algorithm
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pprint import pprint
from typing import TypeAlias, NamedTuple, Literal
from icecream import ic
from loguru import logger
import enum


# typing
TreePath: TypeAlias = tuple


# core


class actions:
    def Append():
        """Append to last position"""

    def Insert(index: int = 0):
        """Inset at position @index. Shifts list"""

    def KeepThis():
        """Keep old side"""

    def KeepOther():
        """Keep new side"""

    def Merge(levels: int = -1):
        """-1 for recursive"""


# what to do with conflict inside specific types
global_conflict_policy_profiles = {
    "dict": {
        "terminal": actions.KeepThis(),
        "dict": actions.Merge(-1),
        "list": True,
    },
    "sequence": {
        "terminal": actions.Append(),
        "dict": actions.Append(),
        "list": actions.Append(),
    },
    "set": {
        "terminal": actions.KeepThis(),
        "dict": actions.KeepThis(),
        "list": actions.KeepThis(),
    },
}


class ScopeParser:
    @staticmethod
    def pop_from_list(list_data: list):
        ...

    @staticmethod
    def pop_from_dict(dict_data: dict):
        ...


@dataclass
class MergePolicy:
    """
    Responsible for managing global, scope and key-specific policies
    """

    merge: bool = True
    merge_unique: bool = True
    dict_id_key_override: str | None = None

    def pop_and_load_list_scope(self, list_data: list):
        """Pop merge-marks from list and load into old object."""
        i = len(list_data) - 1
        while i >= 0:
            try:
                value = list_data[i].lower()
            except AttributeError:
                i -= 1
                continue

            decrement = 2
            if value in ("dynaconf_merge",):
                list_data.pop(i)
                self.merge = True
            elif value in ("dynaconf_merge=false",):
                list_data.pop(i)
                self.merge = False
            elif value in ("dynaconf_merge_unique",):
                list_data.pop(i)
                self.merge_unique = True
            elif value.startswith("@dict_id_key"):
                list_data.pop(i)
                self.dict_id_key_override = value[value.find("=") + 1 :]

            elif value in ("@empty"):
                list_data[i] = None
            else:
                decrement = 1
            i -= decrement

    def pop_and_load_dict_scope(self, dict_data: dict):
        """Pop merge-marks from dict and load into old object."""
        scope_merge = dict_data.get(
            "dynaconf_merge",
        )
        if scope_merge:
            self.merge = scope_merge


class MergeDispatcher:
    """
    Responsible for choosing which merge_fn to use according to some context.
    """


class PseuIdGenerator:
    """Generates pseudo id for non-hashable types using custom strategies"""

    def generate_id(self, object: object):
        ...


class EMPTY:
    def __repr__(self):
        # return "\u2205"
        return "EMPTY"


class Sentinel(enum.Enum):
    EMPTY = EMPTY()


def merge_dict(old, new, merge_policy: MergePolicy = None, tree_path: TreePath = None):
    intersection = old.keys() & new.keys()
    old_only = old.keys() - intersection
    new_only = new.keys() - intersection

    pprint(f"{intersection=}")
    pprint(f"{old_only=}")
    pprint(f"{new_only=}")


def merge_terminal(old, new, merge_policy: MergePolicy, tree_path: TreePath):
    ...


def keep_old(old, new, *args, **kwrgs):
    return old


def keep_new(old, new, *args, **kwrgs):
    return new

def pseudo_hash(container: dict, pseudo_key=None):
    return uuid.uuid4()


class PseudoIdStrategies:
    @staticmethod
    def use_index(unique_name: str, container: list, *args, **kwargs) -> dict:
        return {i: i for i, e in enumerate(container)}

    @staticmethod
    def use_value_hash(
        unique_name: str,
        container: list,
        dict_key_override: str | None = None,
        **kwargs,
    ) -> dict:
        """
        If value is dict
        - lookup for id markup inside it. e.g. [1, {dynaconf_id="foo", ...}, 3]
        - use incremental id (__old_i__, __new_i__) (...), i++ (unique inside scope)
        """
        return_dict = {}
        dict_key_name = "dynaconf_id"
        pop_key_id = True
        if dict_key_override is not None:
            dict_key_name = dict_key_override
            pop_key_id = False

        incremental_id_counter = 0
        incremental_id_template = "__{name}_{counter}__"
        for i, e in enumerate(container):
            if isinstance(e, dict):
                pseudo_id_name = e.get(dict_key_name)
                if pop_key_id:
                    e.pop(dict_key_name, None)

                if pseudo_id_name is not None:
                    return_dict[f"{dict_key_name}_{pseudo_id_name}"] = i
                else:
                    return_dict[
                        incremental_id_template.format(
                            name=unique_name, counter=incremental_id_counter
                        )
                    ] = i
            else:
                return_dict[e] = i

        return return_dict


class ShallowDiff(NamedTuple):
    """
    A single-level diff of containers.

    Args:
        identity_key: The key used for id comparision (is a pseudo-key for list items)
        diff_pair: A pair of (old, new) values
        real_key_pair: A pair of (old-real-key, new-real-key).
            In lists, it's the index. It may differ from identity_key, dependening
            on the pseudo-key generation strategy.
    Examples:
        To understand why it is shallow, notice how it doesn't compare values,
        just keys or pseudo-keys.

        This allows a future diff-interpreter to take give different meaning
        to this, allowing configurable fine-control of the merging process.
        For example, it could take Diff(id_key="a", diff_pair=(1,1)) and merge that
        into "a" as  [1,1] or 2 ("a": [1,2] or "a": [1,2]).

        {a: A, b: B}
        {a: A, b: B, c: C}
        ------------------
        Diff(a,    diff_pair=(A, A),        real_key_pair=(a, a))
        Diff(b,    diff_pair=(B, B),        real_key_pair=(a, a))
        Diff(c,    diff_pair=(EMPTY, B),    real_key_pair=(a, a))

        # list merge [pseudo-key.use_index]
        # uses positional comparision (by index)
        [1, {...}, 3]
        [3, {...}, 1]
        ------------------
        Diff(0,    diff_pair=(1, 3),        real_key_pair=(0, 0))
        Diff(1,    diff_pair=({...}, {...}),        real_key_pair=(1, 1))
        Diff(2,    diff_pair=(3, 1),    real_key_pair=(2, 2))

        # list merge [pseudo-key.use_value_hash]
        # - generates id_key from value_hash.
        # - uses random uuid4 for unhashable values.
        [1, {...}, 3]
        [3, {...}, 1]
        ------------------
        Diff(id_key=1,        diff_pair=(1, 1),            real_key_pair=(0, 2))
        Diff(id_key=3,        diff_pair=(3, 3),            real_key_pair=(2, 0))
        Diff(id_key=uuid-a,   diff_pair=({...}, EMPTY),    real_key_pair=(a, a))
        Diff(id_key=uuid-b,   diff_pair=(EMPTY, {...}),    real_key_pair=(a, a))

        # list merge [pseudo-key.use_value_hash + special dict-id]
        # - generates id_key from value_hash
        # - uses id_mark inside dict to produce it's pseudo id_key
        [1, {id_mark=x, ...}, 3]
        [3, {id_mark=x, ...}, 1]
        ------------------
        Diff(id_key=1,    diff_pair=(1, 1),            real_key_pair=(0, 2))
        Diff(id_key=3,    diff_pair=(3, 3),            real_key_pair=(2, 0))
        Diff(id_key=x,    diff_pair=({...}, {...}),    real_key_pair=(a, a))
    """

    id_key: str
    diff_pair: tuple
    real_key_pair: tuple


@dataclass
class DiffList:
    _diff_list: list = field(default_factory=list)

    def append(self, diff: ShallowDiff):
        self._diff_list.append(diff)

    def get(
        self,
        filter_attr: Literal["id_key"]
        | Literal["diff_pair"]
        | Literal["real_key_pair"] = None,
    ):
        """
        Return list of ShallowDiff or subset of its attr (defined in filter_attr)
        Args:
            filter_attr: return only the specified diff.attr from the diffs
        """
        if filter_attr is not None:
            return (getattr(diff, filter_attr) for diff in self._diff_list)
        return self._diff_list

    def sort(self, by_attr: str = "id_key", by_attr_secondary: str = None):
        """Sort this diff_list in-place by key"""
        self._diff_list.sort(key=lambda item: str(getattr(item, by_attr)))
        return self


class Differ:
    pseudo_id_strategies = PseudoIdStrategies
    EMPTY = Sentinel.EMPTY.value

    @staticmethod
    def list_scope(
        old,
        new,
        merge_policy: MergePolicy = None,
        tree_path: TreePath = None,
        pseudo_id_strategy=None,
    ):
        """Return a ShallowDiff lists (old,new)."""
        pseudo_id_mapper = pseudo_id_strategy or PseudoIdStrategies.use_index
        merge_policy = merge_policy or MergePolicy()
        merge_policy.pop_and_load_list_scope(new)

        # maps {old.pseudo_id -> old.index},
        # - pseudo_id is a generated id from the list-item (for identify comparision)
        # - index is the address of the item in the original list
        old_pseudo_id_map = pseudo_id_mapper(
            "old", old, dict_key_override=merge_policy.dict_id_key_override
        )
        new_pseudo_id_map = pseudo_id_mapper(
            "new", new, dict_key_override=merge_policy.dict_id_key_override
        )

        union_keys = old_pseudo_id_map.keys() | new_pseudo_id_map.keys()

        diffs = DiffList()
        for id_key in union_keys:
            # get index from pseudo_id
            old_index_key = old_pseudo_id_map.get(id_key, None)
            new_index_key = new_pseudo_id_map.get(id_key, None)

            # get value from index
            old_value = old[old_index_key] if old_index_key is not None else None
            new_value = new[new_index_key] if new_index_key is not None else None

            # populate ShallowDiff
            diff_pair = (old_value, new_value)
            real_key_pair = (old_index_key, new_index_key)

            diff_object = ShallowDiff(id_key, diff_pair, real_key_pair)
            diffs.append(diff_object)
        return diffs




def diff_report(name, old, new, diff_fn, **kwargs):
    print()
    print(f"> {name}")
    ic(old)
    ic(new)
    out = list(diff_fn(old, new, **kwargs).sort().get(filter_attr="diff_pair"))
    ic(out)


def list_merge_use_index_cases():
    logger.info("list_merge(a,b) with use_index")
    diff_report(
        "list mode: positional",
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional new < old",
        [1, 2, 3],
        [3, 2],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list mode: positional + old < new",
        [3, 2],
        [1, 2, 3],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + dicts",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )

    diff_report(
        "list-mode: positional + @empty pads",
        [1, {"a": "B"}, 3],
        ["@empty", {"a": "B"}, "@empty"],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_index,
    )


def list_merge_use_value_hash_cases():
    diff_report(
        "list-mode: value hash + hashable values only",
        [1, 2, 3],
        [2, 1, 0],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict(annonymous)",
        [1, {"a": "B"}, 3],
        [3, {"a": "B"}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_default",
        [1, 3, {"a": "B", "dynaconf_id": 1}],
        [3, {"a": "B", "dynaconf_id": 1}, 1],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )

    diff_report(
        "list-mode: value hash + dict + dict_id_mark_override",
        [1, {"a": "B", "c": "C"}, 3],
        [3, {"a": "B", "d": "D"}, 1, "@dict_id_key=a"],
        Differ.list_scope,
        pseudo_id_strategy=Differ.pseudo_id_strategies.use_value_hash,
    )


if __name__ == "__main__":
    list_merge_use_index_cases()
    list_merge_use_value_hash_cases()
