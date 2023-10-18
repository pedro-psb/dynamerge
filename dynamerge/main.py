from __future__ import annotations


class actions:
    """Just an idea. Not being used"""

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
# NOT BEING USED
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
