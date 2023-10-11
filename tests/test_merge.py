"""
This test uses a special a special Case class, which is a declarative object
that helps setup complex scenarios for simple in==out assertions.

Check the specific case parameters to understand it's the variables in play.
"""
from dynamerge.differ import KeyDiffer, MergePolicy
from dynamerge.merger import Merger
import pytest
from .cases import merge_cases
from icecream import ic


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


@pytest.mark.parametrize("case", param_cases(merge_cases.case_list))
def test_merge_dicts(case: merge_cases.MergeCase):
    merge_policy = MergePolicy()
    Merger.merge_dict(case.old, case.new, merge_policy)
    assert case.old == case.expected
