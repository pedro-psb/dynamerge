"""
Merge Algorithm
"""
from __future__ import annotations



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


class MergeDispatcher:
    """
    Responsible for choosing which merge_fn to use according to some context.
    """


def merge_dict(old, new, merge_policy: MergePolicy = None, tree_path: TreePath = None):
    ...


def merge_terminal(old, new, merge_policy: MergePolicy, tree_path: TreePath):
    ...


def keep_old(old, new, *args, **kwrgs):
    return old


def keep_new(old, new, *args, **kwrgs):
    return new
