"""
This test uses a special a special Case class, which is a declarative object
that helps setup complex scenarios for simple in==out assertions.

Check the specific case parameters to understand it's the variables in play.
"""
from dynamerge.differ import KeyDiffer, MergePolicy, DiffUtils
import pytest
from .cases import diff_list, diff_dict


@pytest.fixture(autouse=True)
def pad():
    print()
    yield


def param_cases(cases):
    """Utility to return a list of pytest.param cases"""
    param_cases = []
    for case in cases:
        case_name = case.name.replace(" ", "-").replace(":", "-")
        param_cases.append(pytest.param(case, id=case_name))

    return param_cases


@pytest.mark.parametrize("case", param_cases(diff_list.case_list))
def test_diff_lists(case: diff_list.DiffCase):
    merge_policy = case.merge_policy or MergePolicy()
    diffs = KeyDiffer.diff_list(case.old, case.new, merge_policy, case.pseudo_id)
    assert DiffUtils.sort_diff_list(diffs) == DiffUtils.sort_diff_list(case.exp)


@pytest.mark.parametrize("case", param_cases(diff_dict.case_list))
def test_diff_dict(case: diff_dict.DiffCase):
    merge_policy = case.merge_policy or MergePolicy()
    diffs = KeyDiffer.diff_dict(case.old, case.new, merge_policy)
    assert DiffUtils.sort_diff_list(diffs) == DiffUtils.sort_diff_list(case.exp)
