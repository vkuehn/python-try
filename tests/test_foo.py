import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_try.foo import foo


def test_foo():
    assert foo(bar="bar") == "foo received bar"
