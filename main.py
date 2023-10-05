"""
Merge Algorithm
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pprint import pprint
from typing import TypeAlias, Protocol, Literal, Union, NamedTuple

from loguru import logger


# typing
TreePath: TypeAlias = tuple


class merge_fn(Protocol):
    def __call__(self, old, new, merge_policy: MergePolicyManager, tree_path: TreePath):
        ...


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
        # breakpoint()
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
                list_data[i] = Sentinel.EMPTY
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

    def get_merge_fn(cls, merge_policy: MergePolicy, tree_path: TreePath) -> merge_fn:
        """Return a merge_fn according to context"""
        return


class PseuIdGenerator:
    """Generates pseudo id for non-hashable types using custom strategies"""

    def generate_id(self, object: object):
        ...


import enum


class Sentinel:
    EMPTY = "<EMPTY>"


class EMPTY:
    """TODO make this a class singleon"""

    def __repr__(self):
        return "EMPTY"


def merge_dict(old, new, merge_policy: MergePolicy = None, tree_path: TreePath = None):
    intersection = old.keys() & new.keys()
    old_only = old.keys() - intersection
    new_only = new.keys() - intersection

    pprint(f"{intersection=}")
    pprint(f"{old_only=}")
    pprint(f"{new_only=}")


def pseudo_hash(container: dict, pseudo_key=None):
    return uuid.uuid4()


class IdToIndexMapStrategies:
    @staticmethod
    def use_index(container: list, *args, **kwargs) -> dict:
        return {i: i for i, e in enumerate(container)}

    @staticmethod
    def use_value_hash(
        container: list, dict_key_id_override: str | None = None
    ) -> dict:
        """
        If value is dict
        - lookup for id markup inside it. e.g. [1, {dynaconf_id="foo", ...}, 3]
        - use uuid (assume dict in "new" doesn't have an identity pair in "old".
        """
        return_dict = {}
        pop_key_id = False
        if dict_key_id_override is None:
            dict_key_id_override = "dynaconf_id"
            pop_key_id = True

        for i, e in enumerate(container):
            if isinstance(e, dict):
                id_mark = (
                    e.pop(dict_key_id_override, None)
                    if pop_key_id
                    else e.get(dict_key_id_override)
                )
                if id_mark:
                    return_dict[f"{dict_key_id_override}_{id_mark}"] = i
                else:
                    return_dict[uuid.uuid4()] = i
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


def diff_list(
    old,
    new,
    merge_policy: MergePolicy = None,
    tree_path: TreePath = None,
    dict_gen_strategy=None,
):
    """Return a ShallowDiff lists (old,new)."""
    print()
    logger.debug("merging")
    pprint(old)
    pprint(new)
    print()

    _id_to_index_mapper = dict_gen_strategy or IdToIndexMapStrategies.use_index
    _merge_policy = merge_policy or MergePolicy()
    _merge_policy.pop_and_load_list_scope(new)

    # maps {old.pseudo_id -> old.index},
    # - pseudo_id is a generated id from the list-item (for identify comparision)
    # - index is the address of the item in the original list
    _old = _id_to_index_mapper(old, _merge_policy.dict_id_key_override)
    _new = _id_to_index_mapper(new, _merge_policy.dict_id_key_override)

    intersection_keys = _old.keys() & _new.keys()
    old_only_keys = _old.keys() - intersection_keys
    new_only_keys = _new.keys() - intersection_keys

    print("[conflicts]")
    for id_key in intersection_keys:
        old_index_key = _old[id_key]
        new_index_key = _new[id_key]

        diff_pair = (old[old_index_key], new[new_index_key])
        real_key_pair = (old_index_key, new_index_key)
        diff_object = ShallowDiff(id_key, diff_pair, real_key_pair)
        print(f"{diff_object}")

    print("[old_only]")
    for id_key in old_only_keys:
        old_index_key = _old[id_key]
        diff_tuple = (old[old_index_key], None)
        print(f"{diff_tuple}")

    print("[new_only]")
    for id_key in new_only_keys:
        new_index_key = _new[id_key]
        diff_tuple = (None, new[new_index_key])
        print(f"{diff_tuple}")


def merge_terminal(old, new, merge_policy: MergePolicy, tree_path: TreePath):
    ...


def keep_old(old, new, *args, **kwrgs):
    return old


def keep_new(old, new, *args, **kwrgs):
    return new


def list_merge_use_index_cases():
    logger.info("list_merge(a,b) with use_index")
    list_a = [1, 2, 3, 4]
    list_b = [3, 2, 1, 0]
    shallow_diff_list(list_a, list_b)

    list_a = [1, {"a": "B"}, 3]
    list_b = [3, {"a": "B"}, 1]
    shallow_diff_list(list_a, list_b)

    list_a = [1, {"a": "B"}, 3]
    list_b = ["@empty", {"a": "B"}, "@empty"]
    shallow_diff_list(list_a, list_b)


def list_merge_use_value_hash_cases():
    logger.info("list_merge(a,b) with use_value_hash")
    list_a = [1, 2, 3, 4]
    list_b = [3, 2, 1, 0]
    shallow_diff_list(
        list_a, list_b, dict_gen_strategy=IdToIndexMapStrategies.use_value_hash
    )

    list_a = [1, {"a": "B"}, 3]
    list_b = [3, {"a": "B"}, 1]
    shallow_diff_list(
        list_a, list_b, dict_gen_strategy=IdToIndexMapStrategies.use_value_hash
    )

    list_a = [1, {"a": "B", "dynaconf_id": 1}, 3]
    list_b = [3, {"a": "B", "dynaconf_id": 1}, 1]
    shallow_diff_list(
        list_a, list_b, dict_gen_strategy=IdToIndexMapStrategies.use_value_hash
    )

    list_a = [1, {"a": "B", "c": "C"}, 3]
    list_b = [3, {"a": "B", "d": "D"}, 1, "@dict_id_key=a"]
    shallow_diff_list(
        list_a, list_b, dict_gen_strategy=IdToIndexMapStrategies.use_value_hash
    )


if __name__ == "__main__":
    # list_merge_use_index_cases()
    list_merge_use_value_hash_cases()
