import importlib.metadata
import pathlib

import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("nzshm_rupture_widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class Widget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    _camera = traitlets.Dict().tag(sync=True)
    data = traitlets.List().tag(sync=True)
    width = traitlets.Unicode('100%').tag(sync=True, o=True)
    height = traitlets.Unicode('400px').tag(sync=True, o=True)
    selection = traitlets.Int(0).tag(sync=True)
    extrusion = traitlets.Float(0).tag(sync=True)

def rupture_map(data, selection=0, extrusion=0):
    if isinstance(data, list):
        return Widget(data=data, selection=selection, extrusion=extrusion)
    else:
        return Widget(data=[data], selection=0, extrusion=extrusion)
