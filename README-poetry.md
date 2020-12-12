## Porting to Poery TODO

- [SOLVED] Package extras is not working. Not able to defint art, display, yaml, etc.
  plugin extras.
  https://stackoverflow.com/questions/60971502/python-poetry-how-to-install-optional-dependencies

    - `poetry add --optional` each dep that can then be manually added to ...
        ```toml
        [tool.poetry.extras]
        yaml-plugin = ["ruamel.yaml"]
        display-plugin = ["grako"]
        art-plugin = ["Pillow", "pylast", "requests"]
        ```
