import importlib.metadata
import pathlib

import anywidget
import traitlets
from ipywidgets import Box, HTML, jslink, GridBox, Layout, DOMWidget

try:
    __version__ = importlib.metadata.version("nzshm_rupture_widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class CesiumWidget(anywidget.AnyWidget):
    """
    A map widget encapsulating a CesiumJS Viewer for displaying 3D GeoJSON data.

    GeoJSON styling:
        CesiumJS supports [simplestyle](https://github.com/mapbox/simplestyle-spec/tree/master/1.1.0) properties in a Feature.

        Additionally, `CesiumWidget` supports a `Leaflet`-inspired `style` property with the folling sub-properties:
        - stroke: whether lines should be drawn
        - color: line color
        - weight: line thickness
        - opacity: line opacity
        - fill: whether a polygon should have a fill
        - fillColor: polygon fill color
        - fillOpacity: polygon fill opacity
        - extrusion: clamps polygons to the ground and extrudes them to this height in meters

        Note that this means that a `fill` value directly in the properties is polygon fill color, while a `fill` in
        the `style` property is a boolean that switches fill on or off.

    Attributes:
        data (list):
            a list of GeoJSON dicts to be displayed on the map. Modifying this attribute after the map has
            been rendered will not have an effect.
        selection (int):
            determines which entry of `data` should be displayed. If set to -1, all will be displayed.
        hover_style (dict):
            a style to apply to polygons when the mouse hovers over them. Supported are `color`, `weight`, `opacity`, `fillColor`, `fillOpacity`.
        no_info (bool):
            suppresses Cesium's built-in GeoJSON properties pop-ups.
        globe_opacity (float):
            allows for the adjustment of globe opacity to better inspect underground geometry. Note that
            a value of 1 causes all GeoJSON to be rendered on top of the globe.

    """

    _esm = pathlib.Path(__file__).parent / "static" / "MapWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    _camera = traitlets.Dict().tag(sync=True)
    data = traitlets.List().tag(sync=True)
    selection = traitlets.Int(0).tag(sync=True)
    hover_style = traitlets.Dict().tag(sync=True)
    no_info = traitlets.Bool(False).tag(sync=True)
    globe_opacity = traitlets.Float(1).tag(sync=True)
    _hover_callback = None
    _on_msg_set = False

    def _on_msg_handler(self, widget, msg, buffer):
        if msg["msg"] == "pick" and self._hover_callback is not None:
            self._hover_callback(msg)

    def on_hover(self, callback):
        """
        Registers a `callback` that is invoked when the mouse hovers over a new GeoJSON entity.
        Parameters:
            callback (function):
            will be called with events of the structure:
            {"msg" : "pick", "source" : "entity", "properties" : {...}}
        """
        self._hover_callback = callback
        if not self._on_msg_set:
            self.on_msg(self._on_msg_handler)
            self._on_msg_set = True

    def go_home(self):
        """
        Causes the map to navigate "home", which is the extent of the currently selected GeoJSON.
        """
        self.send({"action": "home"})


class SliderWidget(anywidget.AnyWidget):
    """
    A slider widget with step buttons.

    Attributes:
        min (int):
            The minimum value
        max (int):
            The maximum value
        value (int):
            The value
    """

    _esm = pathlib.Path(__file__).parent / "static" / "SliderWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    min = traitlets.Int(0).tag(sync=True)
    max = traitlets.Int(10).tag(sync=True)
    value = traitlets.Int(0).tag(sync=True)


class FullScreenWidget(anywidget.AnyWidget):
    """
    A button widget that sets the nearest ancestor with the `fullScreenTarget` class to fullscreen.
    """

    _esm = pathlib.Path(__file__).parent / "static" / "FullScreenWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"


class HomeWidget(anywidget.AnyWidget):
    """
    A button widget that calls the `go_home()` method on a `CesiumWidget`.
    """

    _esm = pathlib.Path(__file__).parent / "static" / "HomeWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"

    # see https://github.com/manzt/anywidget/issues/650#issuecomment-2286472536
    def __init__(self, map: CesiumWidget):
        """
        Parameters
            map (CesiumWidget):
        """
        super().__init__()
        self.on_msg(lambda widget, msg, buffer: map.go_home())


class ValueButtonWidget(anywidget.AnyWidget):
    """
    A button widget that cycles through a list of preset values.

    Attributes:
        values (list):
            a list of values to cycle through
        value (any):
            the current value
        icon (string):
            a CSS class. Classes already assigned to the HTML element are `fa` and `controlButton3DMap`
    """

    _esm = pathlib.Path(__file__).parent / "static" / "ValueButtonWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    values = traitlets.List([0, 1]).tag(sync=True)
    value = traitlets.Any(0).tag(sync=True)
    icon = traitlets.Unicode("fa-exclamation").tag(sync=True)


def transparency_button(map_widget: CesiumWidget, values: list):
    """
    Creates a button widget that switches the `globe-opacity` of a `CesiumWidget` between
    the specified `values`.

    Parameters:
        map_widget (CesiumWidget):
            the map
        values (list):
            a list of possible opacity values between 0 and 1

    Returns:
        ValueButtonWidget:
            the button widget
    """
    widget = ValueButtonWidget(values=values, value=values[0], icon="fa-eye")
    jslink((map_widget, "globe_opacity"), (widget, "value"))
    return widget


def legend(title: str, values: dict):
    """
    Creates a legend widget.

    Args:
        title (str):
            The title of the legend
        values (dict):
            A mapping from `key` to CSS color `value`

    Returns:
        HTML:
            A static widget displaying the legend.
    """
    html = HTML()
    value = f"<b>{title}</b><br/>"
    for key, val in values.items():
        value += f'<div><i style="background-color: {val};"></i> {key}</div>'
    html.value = value
    html.add_class("mapLegend")
    return html


def selection_slider(map_widget: CesiumWidget):
    """
    A slider that can be used to switch between different GeoJSON objects of `map_widget`.

    Args:
        map_widget (CesiumWidget):
            a map with more than one GeoJSON object

    Returns:
        SliderWidget:
            A slider widget that is linked to the `map_widget`
    """
    slider_widget = SliderWidget(min=0, max=len(map_widget.data) - 1, value=0)
    jslink((map_widget, "selection"), (slider_widget, "value"))
    return slider_widget


class MapLayoutBuilder:
    """
    Creates a layout for adding widgets to a map.
    This class is not a widget itself. Call `build()` to create the widget.
    """

    cesium: None
    grid_box: None

    def __init__(self, cesium: CesiumWidget):
        """
        Parameters:
            cesium (CesiumWidget):
                the map widget. All other widgets will be overlayed on top of this widget.
        """
        self.cesium = cesium
        self.grid_box = None
        if not cesium.layout:
            cesium.layout = Layout(grid_area="1 / 1 / -1 / -1")
        else:
            cesium.layout.grid_area = "1 / 1 / -1 / -1"

        self.widgets = {
            "top-left": [],
            "bottom-left": [],
            "top-right": [],
            "bottom-right": [],
        }

    def add(self, widget: DOMWidget, position="bottom-right"):
        """
        Adds a widget to layout.

        Args:
            widget (DomWidget):
                The widget to be added
            position (str, optional):
                The position where the widget should be displayed. Possible values are
                `top-left`, `bottom-left`, `top-right`, `bottom-right` (default).
        """
        self.widgets[position].append(widget)

    def build(self):
        """
        Creates a widget that contains all added widgets.
        Returns:
            GridBox:
                The widget.
        """
        if self.grid_box:
            return self.grid_box

        positions = [self.cesium]
        if self.widgets["top-left"]:
            bar = Box(self.widgets["top-left"])
            bar.add_class("mapLeftBar")
            bar.add_class("mapTopLeft")
            positions.append(bar)
        if self.widgets["bottom-left"]:
            bar = Box(self.widgets["bottom-left"])
            bar.add_class("mapLeftBar")
            bar.add_class("mapBottomLeft")
            positions.append(bar)
        if self.widgets["top-right"]:
            bar = Box(self.widgets["top-right"])
            bar.add_class("mapRightBar")
            bar.add_class("mapTopRight")
            positions.append(bar)
        if self.widgets["bottom-right"]:
            bar = Box(self.widgets["bottom-right"])
            bar.add_class("mapRightBar")
            bar.add_class("mapBottomRight")
            positions.append(bar)

        self.grid_box = GridBox(
            children=positions,
            layout=Layout(
                width="100%",
                height="400px",
                grid_template_rows="50px auto 50px",
                grid_template_columns="200px auto 300px",
            ),
        )
        self.grid_box.add_class("fullScreenTarget")
        return self.grid_box


def decorate(cesium: CesiumWidget, home=True, fullscreen=True, transparency=True, slider=True):
    """
    Creates a MapLayoutBuilder with default widgets.
    Args:
        cesium (CesiumWidget): 
            the CesiumWidget
        home (bool, optional):
            whether to add a home button. Defaults to True.
        fullscreen (bool, optional): 
            whether tpo add a full screen button. Defaults to True.
        transparency (bool, optional): 
            whether to add a transparency button. Defaults to True.
        slider (bool, optional): 
            whether to add a slider. Defaults to True.

    Returns:
        MapLayoutBuilder:
            a `MapLayoutBuilder` with the default widgets.
    """
    layout = MapLayoutBuilder(cesium)
    if home:
        layout.add(HomeWidget(cesium), "top-left")
    if fullscreen:
        layout.add(FullScreenWidget(), "top-left")
    if transparency:
        layout.add(transparency_button(cesium, [1, 0.8, 0.3]), "top-left")
    if slider and len(cesium.data) > 1:
        layout.add(selection_slider(cesium), "bottom-right")

    return layout

def geojson_3d_map(data:list):
    cesium = CesiumWidget(data=data)
    layout_builder = decorate(cesium)
    return layout_builder.build()
