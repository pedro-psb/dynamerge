from dynamerge.differ import KeyDiffer, KeyDiff
from icecream import ic
import pytest


@pytest.fixture(autouse=True)
def pad():
    print()
    yield


def param(name: str, *args):
    return pytest.param(*args, id=name)


cases_args = "old, new, expected, pseudo_id_strategy"
cases = [
    param(
        "mode-positional",
        [1, {"a": "A", "b": "B"}, 3],
        [1, {"a": "A", "b": "B"}, 3],
        [
            KeyDiff(0, (1, 1), (0, 0)),
            KeyDiff(1, ({"a": "A", "b": "B"}, {"a": "A", "b": "B"}), (1, 1)),
            KeyDiff(2, (3, 3), (2, 2)),
        ],
        KeyDiffer.pseudo_id_strategies.use_index,
    ),
    param(
        "mode-unique--without-dict-id",
        [1, {"a": "A", "b": "B"}, 3],
        [1, {"a": "A", "b": "B"}, 3],
        [
            KeyDiff(0, (1, 1), (0, 0)),
            KeyDiff(1, ({"a": "A", "b": "B"}, None), (1, 1)),
            KeyDiff(1, ({"a": "A", "b": "B"}, None), (1, 1)),
            KeyDiff(2, (3, 3), (2, 2)),
        ],
        KeyDiffer.pseudo_id_strategies.use_value_hash,
    ),
]


@pytest.mark.parametrize(
    cases_args,
    cases,
)
def test_diff_list_basic(old, new, pseudo_id_strategy, expected):
    diff_list = KeyDiffer.list_scope(
        old,
        new,
        pseudo_id_strategy=pseudo_id_strategy,
    )
    assert diff_list == expected
