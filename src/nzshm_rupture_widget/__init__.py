import importlib.metadata
import pathlib

import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("nzshm_rupture_widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class MapWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    _camera = traitlets.Dict().tag(sync=True)
    data = traitlets.List().tag(sync=True)
    width = traitlets.Unicode('100%').tag(sync=True, o=True)
    height = traitlets.Unicode('400px').tag(sync=True, o=True)
    selection = traitlets.Int(0).tag(sync=True)

class SliderWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "SliderWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    min = traitlets.Int(0).tag(sync=True)
    max = traitlets.Int(10).tag(sync=True)
    value = traitlets.Int(0).tag(sync=True)

def rupture_map(data, selection=0):
    if isinstance(data, list):
        return MapWidget(data=data, selection=selection)
    else:
        return MapWidget(data=[data], selection=0)
