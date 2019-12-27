import eyed3.plugins
from eyed3 import log
from eyed3.plugins.jsontag import audioFileToJson

_have_yaml = False
try:
    import ruamel.yaml as yaml
    _have_yaml = True
except ImportError:
    try:
        import yaml
        _have_yaml = True
    except ImportError:
        log.info("yaml plugin: Install `ruamel.yaml` or `pyyaml` for YAML support.")


if _have_yaml:

    class YamlTagPlugin(eyed3.plugins.LoaderPlugin):
        NAMES = ["yaml"]
        SUMMARY = "Outputs all tags as YAML."

        def __init__(self, arg_parser):
            super().__init__(arg_parser, cache_files=True, track_images=False)

        def handleFile(self, f, *args, **kwargs):
            super().handleFile(f)
            if self.audio_file and self.audio_file.info and self.audio_file.tag:
                print(yaml.safe_dump(audioFileToJson(self.audio_file),
                                     indent=2, default_flow_style=False,
                                     explicit_start=True))
