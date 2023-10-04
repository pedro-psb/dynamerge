"""
Merge Algorithm
"""
from __future__ import annotations
from typing import TypeAlias, Protocol, Literal
from dataclasses import dataclass

# typing
TreePath: TypeAlias = tuple


class merge_fn(Protocol):
    def __call__(
        self,
        this,
        other,
        merge_policy: MergePolicyManager,
        tree_path: TreePath
    ):
        ...


# core

class actions:
    def Append():
        """Append to last position"""

    def Insert(index: int = 0):
        """Inset at position @index. Shifts list"""

    def KeepThis():
        """Keep this side"""

    def KeepOther():
        """Keep other side"""

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
    }
}


@dataclass
class MergePolicy:
    """
    Responsible for managing global, scope and key-specific policies
    """
    merge: bool = True
    merge_unique: bool = True

    def pop_and_load_list_scope(self, list_data: list):
        """Pop merge-marks from list and load into this object."""
        i = len(list_data)
        while i >= 0:
            value = list_data[i].lower()
            decrement = 2
            if value in ("dynaconf_merge",):
                self.merge = True
            elif value in ("dynaconf_merge=false",):
                self.merge = False
            elif value in ("dynaconf_merge_unique",):
                self.merge_unique = False
            else:
                decrement = 1
            i -= decrement

    def pop_and_load_dict_scope(self, dict_data: dict):
        """Pop merge-marks from dict and load into this object."""
        scope_merge = dict_data.get("dynaconf_merge", )
        if scope_merge:
            self.merge = scope_merge


class MergeDispatcher:
    """
    Responsible for choosing which merge_fn to use according to some context.
    """

    def get_merge_fn(
        cls,
        merge_policy: MergePolicy,
        tree_path: TreePath
    ) -> merge_fn:
        """Return a merge_fn according to context"""
        return


class PseuIdGenerator:
    """Generates pseudo id for non-hashable types using custom strategies"""

    def generate_id(self, object: object):
        ...


def merge_dict(
        this,
        other,
        merge_policy: MergePolicy,
        tree_path: TreePath):
    intersection = this.keys() & other.keys()
    this_only = this.keys() - intersection
    other_only = other.keys() - intersection

    print(intersection)
    print(this_only)
    print(other_only)


def merge_list(
        this,
        other,
        merge_policy: MergePolicy,
        tree_path: TreePath):
    ...
    ...


def merge_terminal(
        this,
        other,
        merge_policy: MergePolicy,
        tree_path: TreePath):
    ...


def keep_this(this, other, *args, **kwrgs):
    return this


def keep_other(this, other, *args, **kwrgs):
    return other
