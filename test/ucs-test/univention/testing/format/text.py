"""Format UCS Test results as simple text report."""


import curses
import re
import subprocess
import sys
import time
from typing import IO  # noqa: F401
from weakref import WeakValueDictionary

import univention.config_registry
from univention.testing.codes import TestCodes
from univention.testing.data import TestCase, TestEnvironment, TestFormatInterface, TestResult  # noqa: F401


__all__ = ['Text', 'Raw']


class _Term:  # pylint: disable-msg=R0903
    """Handle terminal formatting."""

    __ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()
    # vt100.sgr0 contains a delay in the form of '$<2>'
    __RE_DELAY = re.compile(br'\$<\d+>[/*]?')

    def __init__(self, term_stream=sys.stdout):  # type: (IO[str]) -> None
        self.COLS = 80  # pylint: disable-msg=C0103
        self.LINES = 25  # pylint: disable-msg=C0103
        self.NORMAL = b''  # pylint: disable-msg=C0103
        for color in self.__ANSICOLORS:
            setattr(self, color, b'')
        if not term_stream.isatty():
            return
        try:
            curses.setupterm()
        except TypeError:
            return
        self.COLS = curses.tigetnum('cols') or 80
        self.LINES = curses.tigetnum('lines') or 25
        self.NORMAL = _Term.__RE_DELAY.sub(b'', curses.tigetstr('sgr0') or b'')
        set_fg_ansi = curses.tigetstr('setaf')
        for color in self.__ANSICOLORS:
            i = getattr(curses, 'COLOR_%s' % color)
            val = set_fg_ansi and curses.tparm(set_fg_ansi, i) or b''
            setattr(self, color, val)


class Text(TestFormatInterface):
    """Create simple text report."""

    __term = WeakValueDictionary()

    def __init__(self, stream=sys.stdout):  # type: (IO[str]) -> None
        super().__init__(stream)
        try:
            self.term = Text.__term[self.stream]
        except KeyError:
            self.term = Text.__term[self.stream] = _Term(self.stream)

    def begin_run(self, environment, count=1):  # type: (TestEnvironment, int) -> None
        """Called before first test."""
        super().begin_run(environment, count)
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"Starting {count} ucs-test at {now} to {environment.log.name}", file=self.stream)
        try:
            ucs_test_version = subprocess.check_output(['/usr/bin/dpkg-query', '--showformat=${Version}', '--show', 'ucs-test-framework']).decode('UTF-8', 'replace')
        except subprocess.CalledProcessError:
            ucs_test_version = 'not installed'
        ucr = univention.config_registry.ConfigRegistry()
        ucr.load()
        print("UCS %s-%s-e%s ucs-test %s" % (ucr.get('version/version'), ucr.get('version/patchlevel'), ucr.get('version/erratalevel'), ucs_test_version), file=self.stream)

    def begin_section(self, section):  # type: (str) -> None
        """Called before each section."""
        super().begin_section(section)
        if section:
            header = f" Section '{section}' "
            line = header.center(self.term.COLS, '=')
            print(line, file=self.stream)

    def begin_test(self, case, prefix=''):  # type: (TestCase, str) -> None
        """Called before each test."""
        super().begin_test(case, prefix)
        title = case.description or case.uid
        title = prefix + title.splitlines()[0]

        cols = self.term.COLS - TestCodes.MAX_MESSAGE_LEN - 1
        if cols < 1:
            cols = self.term.COLS
        while len(title) > cols:
            print(title[:cols], file=self.stream)
            title = title[cols:]
        ruler = '.' * (cols - len(title))
        print(f'{title}{ruler}', end=' ', file=self.stream)
        self.stream.flush()

    def end_test(self, result, end='\n'):  # type: (TestResult, str) -> None
        """Called after each test."""
        reason = result.reason
        msg = TestCodes.MESSAGE.get(reason, reason)

        colorname = TestCodes.COLOR.get(result.reason, 'BLACK')
        color = getattr(self.term, colorname.upper(), b'')

        print('%s%s%s' % (color.decode('ASCII'), msg, self.term.NORMAL.decode('ASCII')), end=end, file=self.stream)
        super().end_test(result)

    def end_section(self):  # type: () -> None
        """Called after each section."""
        if self.section:
            print(file=self.stream)
        super().end_section()

    def format(self, result):  # type: (TestResult) -> None
        """
        >>> te = TestEnvironment()
        >>> tc = TestCase('python/data.py')
        >>> tr = TestResult(tc, te)
        >>> tr.success()
        >>> import io
        >>> s = io.StringIO()
        >>> Text(s).format(tr)
        """
        self.begin_run(result.environment)
        self.begin_section('')
        self.begin_test(result.case)
        self.end_test(result)
        self.end_section()
        self.end_run()


class Raw(Text):
    """Create simple text report with raw file names."""

    def begin_test(self, case, prefix=''):  # type: (TestCase, str) -> None
        """Called before each test."""
        super(Text, self).begin_test(case, prefix)
        title = prefix + case.uid

        cols = self.term.COLS - TestCodes.MAX_MESSAGE_LEN - 2
        if cols < 1:
            cols = self.term.COLS
        while len(title) > cols:
            print(title[:cols], file=self.stream)
            title = title[cols:]
        ruler = '.' * (cols - len(title))
        print(f'{title} {ruler}', end=' ', file=self.stream)
        self.stream.flush()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
