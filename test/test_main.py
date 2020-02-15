import unittest
import deprecation
from eyed3 import main
from . import RedirectStdStreams


def testHelpExitsSuccess():
    with open("/dev/null", "w") as devnull:
        with RedirectStdStreams(stderr=devnull):
            for arg in ["--help", "-h"]:
                try:
                    args, parser = main.parseCommandLine([arg])
                except SystemExit as ex:
                    assert ex.code == 0


def testHelpOutput():
        for arg in ["--help", "-h"]:
            with RedirectStdStreams() as out:
                try:
                    args, parser = main.parseCommandLine([arg])
                except SystemExit as ex:
                    # __exit__ seeks and we're not there yet so...
                    out.stdout.seek(0)
                    assert out.stdout.read().startswith(u"usage:")
                    assert ex.code == 0


def testVersionExitsWithSuccess():
    with open("/dev/null", "w") as devnull:
        with RedirectStdStreams(stderr=devnull):
            try:
                args, parser = main.parseCommandLine(["--version"])
            except SystemExit as ex:
                assert ex.code == 0


def testListPluginsExitsWithSuccess():
    try:
        args, _, _ = main.parseCommandLine(["--plugins"])
    except SystemExit as ex:
        assert ex.code == 0


def testLoadPlugin():
    from eyed3.plugins.classic import ClassicPlugin
    from eyed3.plugins.genres import GenreListPlugin

    args, _, _ = main.parseCommandLine([""])
    assert args.plugin.__class__.__name__ == ClassicPlugin.__name__

    args, _, _ = main.parseCommandLine(["--plugin=genres"])
    assert args.plugin.__class__.__name__ == GenreListPlugin.__name__

    with open("/dev/null", "w") as devnull:
        with RedirectStdStreams(stderr=devnull):
            try:
                args, _ = main.parseCommandLine(["--plugin=DNE"])
            except SystemExit as ex:
                assert ex.code == 1

            try:
                args, _, _ = main.parseCommandLine(["--plugin"])
            except SystemExit as ex:
                assert ex.code == 2


def testLoggingOptions():
    import logging
    from eyed3 import log

    with open("/dev/null", "w") as devnull:
        with RedirectStdStreams(stderr=devnull):
            try:
                _ = main.parseCommandLine(["-l", "critical"])
                assert log.getEffectiveLevel() == logging.CRITICAL

                _ = main.parseCommandLine(["--log-level=error"])
                assert log.getEffectiveLevel() == logging.ERROR

                _ = main.parseCommandLine(["-l", "warning:NewLogger"])
                assert (
                    logging.getLogger("NewLogger").getEffectiveLevel() ==
                    logging.WARNING
                )
                assert log.getEffectiveLevel() == logging.ERROR
            except SystemExit:
                assert not "Unexpected"

            try:
                _ = main.parseCommandLine(["--log-level=INVALID"])
                assert not "Invalid log level, an Exception expected"
            except SystemExit:
                pass


@deprecation.fail_if_not_removed
def testConfigFileDeprecation():
    main._deprecatedConfigFileCheck(None)
