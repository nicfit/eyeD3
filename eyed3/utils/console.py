import os
import struct
import sys
import time

try:
    import fcntl
    import termios
    import signal
    _CAN_RESIZE_TERMINAL = True
except ImportError:
    _CAN_RESIZE_TERMINAL = False

from . import formatSize, formatTime


class AnsiCodes(object):
    _USE_ANSI = False
    _CSI = '\033['

    def __init__(self, codes):
        def code_to_chars(code):
            return AnsiCodes._CSI + str(code) + 'm'

        for name in dir(codes):
            if not name.startswith('_'):
                value = getattr(codes, name)
                setattr(self, name, code_to_chars(value))

                # Add color function
                for reset_name in ("RESET_%s" % name, "RESET"):
                    if hasattr(codes, reset_name):
                        reset_value = getattr(codes, reset_name)
                        setattr(self, "%s" % name.lower(),
                                AnsiCodes._mkfunc(code_to_chars(value),
                                                  code_to_chars(reset_value)))
                        break

    @staticmethod
    def _mkfunc(color, reset):
        def _cwrap(text, *styles):
            if not AnsiCodes._USE_ANSI:
                return text

            s = ''
            for st in styles:
                s += st
            s += color + text + reset
            if styles:
                s += Style.RESET_ALL
            return s
        return _cwrap

    def __getattribute__(self, name):
        attr = super(AnsiCodes, self).__getattribute__(name)
        if (hasattr(attr, "startswith") and
                attr.startswith(AnsiCodes._CSI) and
                not AnsiCodes._USE_ANSI):
            return ""
        else:
            return attr

    def __getitem__(self, name):
        return getattr(self, name.upper())

    @classmethod
    def init(cls, allow_colors):
        cls._USE_ANSI = allow_colors and cls._term_supports_color()

    @staticmethod
    def _term_supports_color():
        if (os.environ.get("TERM") == "dumb" or
                os.environ.get("OS") == "Windows_NT"):
            return False
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class AnsiFore:
    GREY    = 30                                                          # noqa
    RED     = 31                                                          # noqa
    GREEN   = 32                                                          # noqa
    YELLOW  = 33                                                          # noqa
    BLUE    = 34                                                          # noqa
    MAGENTA = 35                                                          # noqa
    CYAN    = 36                                                          # noqa
    WHITE   = 37                                                          # noqa
    RESET   = 39                                                          # noqa


class AnsiBack:
    GREY    = 40                                                          # noqa
    RED     = 41                                                          # noqa
    GREEN   = 42                                                          # noqa
    YELLOW  = 43                                                          # noqa
    BLUE    = 44                                                          # noqa
    MAGENTA = 45                                                          # noqa
    CYAN    = 46                                                          # noqa
    WHITE   = 47                                                          # noqa
    RESET   = 49                                                          # noqa


class AnsiStyle:
    RESET_ALL         = 0                                                 # noqa
    BRIGHT            = 1                                                 # noqa
    RESET_BRIGHT      = 22                                                # noqa
    DIM               = 2                                                 # noqa
    RESET_DIM         = RESET_BRIGHT                                      # noqa
    ITALICS           = 3                                                 # noqa
    RESET_ITALICS     = 23                                                # noqa
    UNDERLINE         = 4                                                 # noqa
    RESET_UNDERLINE   = 24                                                # noqa
    BLINK_SLOW        = 5                                                 # noqa
    RESET_BLINK_SLOW  = 25                                                # noqa
    BLINK_FAST        = 6                                                 # noqa
    RESET_BLINK_FAST  = 26                                                # noqa
    INVERSE           = 7                                                 # noqa
    RESET_INVERSE     = 27                                                # noqa
    STRIKE_THRU       = 9                                                 # noqa
    RESET_STRIKE_THRU = 29                                                # noqa


Fore = AnsiCodes(AnsiFore)
Back = AnsiCodes(AnsiBack)
Style = AnsiCodes(AnsiStyle)


def ERROR_COLOR():
    return Fore.RED


def WARNING_COLOR():
    return Fore.YELLOW


def HEADER_COLOR():
    return Fore.GREEN


class Spinner(object):
    """
    A class to display a spinner in the terminal.

    It is designed to be used with the `with` statement::

        with Spinner("Reticulating splines", "green") as s:
            for item in enumerate(items):
                s.next()
    """
    _default_unicode_chars = "◓◑◒◐"
    _default_ascii_chars = "-/|\\"

    def __init__(self, msg, file=None, step=1,
                 chars=None, use_unicode=True, print_done=True):

        self._msg = msg
        self._file = file or sys.stdout
        self._step = step
        if not chars:
            if use_unicode:
                chars = self._default_unicode_chars
            else:
                chars = self._default_ascii_chars
        self._chars = chars

        self._silent = not self._file.isatty()
        self._print_done = print_done

    def _iterator(self):
        chars = self._chars
        index = 0
        write = self._file.write
        flush = self._file.flush

        while True:
            write("\r")
            write(self._msg)
            write(" ")
            write(chars[index])
            flush()
            yield

            for i in range(self._step):
                yield

            index += 1
            if index == len(chars):
                index = 0

    def __enter__(self):
        if self._silent:
            return self._silent_iterator()
        else:
            return self._iterator()

    def __exit__(self, exc_type, exc_value, traceback):
        write = self._file.write
        flush = self._file.flush

        if not self._silent:
            write("\r")
            write(self._msg)
        if self._print_done:
            if exc_type is None:
                write(Fore.GREEN + ' [Done]\n')
            else:
                write(Fore.RED + ' [Failed]\n')
        else:
            write("\n")
        flush()

    def _silent_iterator(self):
        self._file.write(self._msg)
        self._file.flush()

        while True:
            yield


class ProgressBar(object):
    """
    A class to display a progress bar in the terminal.

    It is designed to be used either with the `with` statement::

        with ProgressBar(len(items)) as bar:
            for item in enumerate(items):
                bar.update()

    or as a generator::

        for item in ProgressBar(items):
            item.process()
    """
    def __init__(self, total_or_items, file=None):
        """
        total_or_items : int or sequence
            If an int, the number of increments in the process being
            tracked.  If a sequence, the items to iterate over.

        file : writable file-like object, optional
            The file to write the progress bar to.  Defaults to
            `sys.stdout`.  If `file` is not a tty (as determined by
            calling its `isatty` member, if any), the scrollbar will
            be completely silent.
        """
        self._file = file or sys.stdout

        if not self._file.isatty():
            self.update = self._silent_update
            self._silent = True
        else:
            self._silent = False

        try:
            self._items = iter(total_or_items)
            self._total = len(total_or_items)
        except TypeError:
            try:
                self._total = int(total_or_items)
                self._items = iter(range(self._total))
            except TypeError:
                raise TypeError("First argument must be int or sequence")

        self._start_time = time.time()

        self._should_handle_resize = (
            _CAN_RESIZE_TERMINAL and self._file.isatty())
        self._handle_resize()
        if self._should_handle_resize:
            signal.signal(signal.SIGWINCH, self._handle_resize)
            self._signal_set = True
        else:
            self._signal_set = False

        self.update(0)

    def _handle_resize(self, signum=None, frame=None):
        self._terminal_width = getTtySize(self._file,
                                          self._should_handle_resize)[1]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._silent:
            if exc_type is None:
                self.update(self._total)
            self._file.write('\n')
            self._file.flush()
            if self._signal_set:
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)

    def __iter__(self):
        return self

    def next(self):
        try:
            rv = next(self._items)
        except StopIteration:
            self.__exit__(None, None, None)
            raise
        else:
            self.update()
            return rv

    def update(self, value=None):
        """
        Update the progress bar to the given value (out of the total
        given to the constructor).
        """
        if value is None:
            value = self._current_value = self._current_value + 1
        else:
            self._current_value = value
        if self._total == 0:
            frac = 1.0
        else:
            frac = float(value) / float(self._total)

        file = self._file
        write = file.write

        suffix = self._formatSuffix(value, frac)
        self._bar_length = self._terminal_width - 37

        bar_fill = int(float(self._bar_length) * frac)
        write("\r|")
        write(Fore.BLUE + '=' * bar_fill + Fore.RESET)
        if bar_fill < self._bar_length:
            write(Fore.GREEN + '>' + Fore.RESET)
            write("-" * (self._bar_length - bar_fill - 1))
        write("|")
        write(suffix)

        self._file.flush()

    def _formatSuffix(self, value, frac):

        if value >= self._total:
            t = time.time() - self._start_time
            time_str = '     '
        elif value <= 0:
            t = None
            time_str = ''
        else:
            t = ((time.time() - self._start_time) * (1.0 - frac)) / frac
            time_str = ' ETA '
        if t is not None:
            time_str += formatTime(t, short=True)

        suffix = ' {0:>4s}/{1:>4s}'.format(formatSize(value, short=True),
                                           formatSize(self._total, short=True))
        suffix += ' ({0:>6s}%)'.format("{0:.2f}".format(frac * 100.0))
        suffix += time_str

        return suffix

    def _silent_update(self, value=None):
        pass

    @classmethod
    def map(cls, function, items, multiprocess=False, file=None):
        """
        Does a `map` operation while displaying a progress bar with
        percentage complete.

        ::

            def work(i):
                print(i)

            ProgressBar.map(work, range(50))

        Parameters:

        function : function
            Function to call for each step

        items : sequence
            Sequence where each element is a tuple of arguments to pass to
            *function*.

        multiprocess : bool, optional
            If `True`, use the `multiprocessing` module to distribute each
            task to a different processor core.

        file : writeable file-like object, optional
            The file to write the progress bar to.  Defaults to
            `sys.stdout`.  If `file` is not a tty (as determined by
            calling its `isatty` member, if any), the scrollbar will
            be completely silent.
        """
        results = []

        if file is None:
            file = sys.stdout

        with cls(len(items), file=file) as bar:
            step_size = max(200, bar._bar_length)
            steps = max(int(float(len(items)) / step_size), 1)
            if not multiprocess:
                for i, item in enumerate(items):
                    function(item)
                    if (i % steps) == 0:
                        bar.update(i)
            else:
                import multiprocessing
                p = multiprocessing.Pool()
                for i, result in enumerate(p.imap_unordered(function, items,
                                                            steps)):
                    bar.update(i)
                    results.append(result)

        return results


def printMsg(s):
    fp = sys.stdout
    assert isinstance(s, str)
    try:
        fp.write("%s\n" % s)
    except UnicodeEncodeError:
        fp.write("%s\n" % str(s.encode("utf-8", "replace"), "utf-8"))
    fp.flush()


def printError(s):
    _printWithColor(s, ERROR_COLOR(), sys.stderr)


def printWarning(s):
    _printWithColor(s, WARNING_COLOR(), sys.stdout)


def printHeader(s):
    _printWithColor(s, HEADER_COLOR(), sys.stdout)


def boldText(s, c=None):
    return formatText(s, b=True, c=c)


def formatText(s, b=False, c=None):
    return ((Style.BRIGHT if b else '') +
            (c or '') +
            s +
            (Fore.RESET if c else '') +
            (Style.RESET_BRIGHT if b else ''))


def _printWithColor(s, color, file):
    assert isinstance(s, str)
    file.write(color + s + Fore.RESET + '\n')
    file.flush()


def cformat(msg, fg, bg=None, styles=None):
    """Format ``msg`` with foreground and optional background. Optional
    ``styles`` lists will also be applied. The formatted string is returned."""
    fg = fg or ""
    bg = bg or ""
    styles = "".join(styles or [])
    reset = Fore.RESET + Back.RESET + Style.RESET_ALL if (fg or bg or styles) \
                                                      else ""

    output = "%(fg)s%(bg)s%(styles)s%(msg)s%(reset)s" % locals()
    return output


def getTtySize(fd=sys.stdout, check_tty=True):
    hw = None
    if check_tty:
        try:
            data = fcntl.ioctl(fd, termios.TIOCGWINSZ, '\0' * 4)
            hw = struct.unpack("hh", data)
        except (OSError, IOError, NameError):
            pass
    if not hw:
        try:
            hw = (int(os.environ.get('LINES')),
                  int(os.environ.get('COLUMNS')))
        except (TypeError, ValueError):
            hw = (78, 25)
    return hw


def cprint(msg, fg, bg=None, styles=None, file=sys.stdout):
    """Calls ``cformat`` and prints the result to output stream ``file``."""
    print(cformat(msg, fg, bg=bg, styles=styles), file=file)


if __name__ == "__main__":
    AnsiCodes.init(True)

    def checkCode(c):
        return (c[0] != '_' and
                "RESET" not in c and
                c[0] == c[0].upper()
               )

    for bg_name, bg_code in ((c, getattr(Back, c))
                             for c in dir(Back) if checkCode(c)):
        sys.stdout.write('%s%-7s%s %s ' %
                         (bg_code, bg_name, Back.RESET, bg_code))
        for fg_name, fg_code in ((c, getattr(Fore, c))
                                 for c in dir(Fore) if checkCode(c)):
            sys.stdout.write(fg_code)
            for st_name, st_code in ((c, getattr(Style, c))
                                     for c in dir(Style) if checkCode(c)):
                sys.stdout.write('%s%s %s %s' %
                                 (st_code, st_name,
                                  getattr(Style, "RESET_%s" % st_name),
                                  bg_code))
        sys.stdout.write("%s\n" % Style.RESET_ALL)

    sys.stdout.write("\n")

    with Spinner(Fore.GREEN + "Phase #1") as spinner:
        for i in range(50):
            time.sleep(.05)
            spinner.next()
    with Spinner(Fore.RED + "Phase #2" + Fore.RESET,
                 print_done=False) as spinner:
        for i in range(50):
            time.sleep(.05)
            spinner.next()
    with Spinner("Phase #3", print_done=False, use_unicode=False) as spinner:
        for i in range(50):
            spinner.next()
            time.sleep(.05)
    with Spinner("Phase #4", print_done=False, chars='.oO°Oo.') as spinner:
        for i in range(50):
            spinner.next()
            time.sleep(.05)

    items = range(200)
    with ProgressBar(len(items)) as bar:
        for item in enumerate(items):
            bar.update()
            time.sleep(.05)

    for item in ProgressBar(items):
        time.sleep(.05)

    progress = 0
    max = 320000000
    with ProgressBar(max) as bar:
        while progress < max:
            progress += 23400
            bar.update(progress)
            time.sleep(.001)
