from eyed3.plugins import *


def test_load():
    plugins = load()
    assert "classic" in  list(plugins.keys())
    assert "genres" in list(plugins.keys())

    assert load("classic") == plugins["classic"]
    assert load("genres") == plugins["genres"]

    assert (load("classic", reload=True).__class__.__name__ ==
            plugins["classic"].__class__.__name__)
    assert (load("genres", reload=True).__class__.__name__ ==
            plugins["genres"].__class__.__name__)

    assert load("DNE") is None

def test_Plugin():
    import argparse
    class MyPlugin(Plugin):
        pass

    p = MyPlugin(argparse.ArgumentParser())
    assert p.arg_group is not None

    # In reality, this is parsed args
    p.start("dummy_args", "dummy_config")
    assert p.args == "dummy_args"
    assert p.config == "dummy_config"

    assert p.handleFile("f.txt") is None
    assert p.handleDone() is None

