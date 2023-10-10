from dynamerge.merger import Merger
from icecream import ic


def merge_report(name: str, old, new, merge_fn, **kwargs):
    print("\n> ", name)
    old = {"root": old}
    new = {"root": new}
    ic(old)
    ic(new)
    out = Merger.merge_dict(old, new, **kwargs)
    ic(out)


def main():
    # case_merge_dicts()
    case_merge_false()


def case_merge_false():
    merge_report(
        "merge_false: root_dict",
        {"a": "A", "b": "B"},
        {"a": "A", "dynaconf_merge": False},
        Merger.merge_dict,
    )

    # merge_report(
    #     "merge_false: nested",
    #     {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}}},
    #     {"b": {"d": {"f": {"g": "G*"}}}, "dynaconf_merge": False},
    #     Merger.merge_dict,
    # )


def case_merge_dicts():
    merge_report(
        "simple merge",
        {"a": "A", "b": "B"},
        {"a": "A*", "c": "C"},
        Merger.merge_dict,
    )

    merge_report(
        "nested dicts: new overrides common keys",
        {"a": "A", "b": {"c": "C", "d": "D"}},
        {"a": "A*", "b": {"c": "C*", "e": "E"}},
        Merger.merge_dict,
    )

    merge_report(
        "nested dicts: new merges different key",
        {"a": "A", "b": {"c": "C", "d": {"e": "E", "f": {"g": "G", "h": "H"}}}},
        {"b": {"d": {"f": {"g": "G*"}}}},
        Merger.merge_dict,
    )


if __name__ == "__main__":
    exit(main())
