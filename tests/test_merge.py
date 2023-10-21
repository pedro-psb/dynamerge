"""
This test uses a special a special Case class, which is a declarative object
that helps setup complex scenarios for simple in==out assertions.

Check the specific case parameters to understand it's the variables in play.
"""
from dynamerge.merge_policy import MergePolicy
from dynamerge.merger import Merger
import pytest
from .cases import merge_dict, merge_list


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


@pytest.mark.parametrize("case", param_cases(merge_dict.cases))
def test_merge_dicts(case: merge_dict.MergeCase):
    merge_policy = MergePolicy()
    # breakpoint()
    Merger().merge_containers(case.old, case.new, merge_policy)
    assert case.old == case.expected


@pytest.mark.parametrize("case", param_cases(merge_list.cases))
def test_merge_lists(case: merge_list.MergeCase):
    merge_policy = MergePolicy()
    Merger().merge_containers(case.old, case.new, merge_policy)
    assert case.old == case.expected
