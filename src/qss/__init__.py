import os
import pathlib
import sys
import tomllib


config = {'instance_control': False}

if getattr(sys, "frozen", False):
    if sys.platform.startswith("win"):
        path = pathlib.Path(os.getenv('LOCALAPPDATA')) / 'fileo/config.toml'
    # elif sys.platform.startswith("linux"):
    #     path = ''
    else:
        path = ''
        raise NotImplemented(f"doesn't support {sys.platform} system")
else:
    path = pathlib.Path(__file__).parent / "fileo.toml"

if path:
    with path.open(mode="rb") as fp:
        config = tomllib.load(fp)
