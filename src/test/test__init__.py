import eyed3


def testLocale():
    assert eyed3.LOCAL_ENCODING
    assert eyed3.LOCAL_ENCODING != "ANSI_X3.4-1968"

    assert eyed3.LOCAL_FS_ENCODING

def testException():

    ex = eyed3.Error()
    assert isinstance(ex, Exception)

    msg = "this is a test"
    ex = eyed3.Error(msg)
    assert ex.message == msg
    assert ex.args == (msg,)

    ex = eyed3.Error(msg, 1, 2)
    assert ex.message == msg
    assert ex.args == (msg, 1, 2)


def test_log():
    from eyed3 import log
    assert log is not None

    log.verbose("Hiya from Dr. Know")
