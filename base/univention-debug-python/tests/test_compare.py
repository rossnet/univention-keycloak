#!/usr/bin/python3

import univention.debug as ud
import univention.debug2 as ud2


def test_compare():
    # type: () -> None
    native = {_ for _ in dir(ud) if not _.startswith('_')}
    native -= {'_debug', 'begin', 'end'}
    python = {_ for _ in dir(ud2) if not _.startswith('_')}
    python -= {'logging', 'DEFAULT', 'print_function'}

    # The C implementation implements everything from the Python version
    assert python <= native, 'Missing C implementation: %s' % (python - native,)

    # The Python implementation implements everything from the C version
    assert native <= python, 'Missing Python implementation: %s' % (native - python,)
