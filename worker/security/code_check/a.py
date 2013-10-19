#testset.py
from nose.tools import ok_, eq_

def test_sum():
    eq_(2+2,4)

def test_failing_sum():
    ok_(2+2 == 3, "Expected failure")

