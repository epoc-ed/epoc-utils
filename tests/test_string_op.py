import pytest

from epoc.string_op import sanitize_label

def test_remove_space():
    assert sanitize_label('Hello World') == 'HelloWorld'

def test_do_not_remove_underline():
    assert sanitize_label('Hello_World') == 'Hello_World'

def test_remove_backslash():
    assert sanitize_label('Hello\\World') == 'HelloWorld'

def test_works_on_empty_string():
    assert sanitize_label('') == ''

def test_works_on_special_characters():
    assert sanitize_label('Hello!@#$%^&*()_+World') == 'Hello_World'

def test_do_not_remove_dash():
    assert sanitize_label('Hello-World') == 'Hello-World'