from __future__ import annotations
from dynamerge.merger import Merger, MergePolicy


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

    def merge(self, other: dict):
        merge_result = self.merger.merge_containers(self, other)


class LazyTree:
    """
    A tree to store (path:lazy-object) data, so it can be re-evaluated
    without recursing the whole three.
    """


class DefaultTree:
    """
    A tree to store (path:default-value) data, so it can be returned as default
    in case the path don't exist in the base_dict.
    """
