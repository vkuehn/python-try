from python_try.foo import foo


def test_foo():
    assert foo(bar="bar") == "foo received bar"
