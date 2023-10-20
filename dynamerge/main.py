from __future__ import annotations

from dynamerge.merger import Merger, MergePolicy, TreePatch


class BaseTree:
    """
    A long living object that store relevant state about the main internal storage,
    that is, the base_dict containing all the settings.
    """

    def __init__(self):
        self.base_dict = {}
        self.lazy_tree = LazyTree()
        self.default_tree = DefaultTree()
        self.merger = Merger
        self.base_merge_policy = MergePolicy()
        self.stats = {"merge_operations_count"}

    def merge(self, other: dict):
        self.merger.merge_containers(self, other)
        merge_result = self.merger.result

        self.stats["merge_operation_count"] += merge_result.merge_operation_count
        self.lazy_tree.update_with_patch(merge_result.tree_patch)

    def get(self, key):
        """
        Get value internally, optionally triggering re-evaluation, pre and pos hooks,
        and fallback to defaults (kind of a hook).
        """

    def set(self, key, value):
        """Shortcut for setting a single key. Trigger a simpe merge."""


class LazyTree:
    """
    A tree to store (path:lazy-object) data, so it can be re-evaluated
    without recursing the whole three.
    """

    def update_with_patch(self, patch: TreePatch):
        """
        Updates self according to operations related to Lazy values, such
        as updating, deleting or adding a LazyValue.
        """


class DefaultTree:
    """
    A tree to store (path:default-value) data, so it can be returned as default
    in case the path don't exist in the base_dict.
    """
