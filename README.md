# py-osm-static-maps

Openstreetmap static maps is a Python lib, CLI and server open source inspired on google static map service. This is a Python rewrite of jperelli/osm-static-maps and should be a drop-in replacement for CLI/HTTP.

## Differences between this and jperelli/osm-static-maps

* Commandline arguments are used as defaults for HTTP requests (allowing you to change the default size, tileserver, enable image compression, etc...)
* Uses a pool of browsers to improve performance, rather than starting one for each request. With the pool idle, my tests are returning a map in ~2.5s on a Pentium N5030
* Uses Firefox instead of Chromium
* Added jpegoptim and pngcrush

## How to use

### 1. CLI

```bash
pip install --user git+https://github.com/NHellFire/py-osm-static-maps.git
osmsm --help
osmsm -g '{"type":"Point","coordinates":[-105.01621,39.57422]}' > map.png
```

### 2. python library

```bash
pip install --user git+https://github.com/NHellFire/py-osm-static-maps.git
```

```python
from osm_static_maps import osmsm

geojson = """{"type":"Point","coordinates":[-105.01621,39.57422]}"""

png = osmsm({"geojson": geojson})
```

### 3. Standalone sample server

```bash
pip install --user git+https://github.com/NHellFire/py-osm-static-maps.git
osmsm serve
```

## API Reference

All parameters have a short and long version. The short version can be used only with the shell CLI. The long version can be used with the library and can be passed to the app server as GET query params, or POST json body (remember to set the header `Content-Type: application/json`)

|   | Parameter | Description | Default Value |
| - | ---- | ---- | ---- |
| g | geojson | geojson object to be rendered in the map | `undefined` |
| f | geojsonfile | filename or url to read geojson data from (use '-' to read from stdin on CLI) | `undefined` |
| H | height | height in pixels of the returned img | `600` |
| W | width | height in pixels of the returned img | `800` |
| c | center | center of the map lon,lat floats string | (center of the geojson) or `'-57.9524339,-34.921779'` |
| z | zoom | zoomlevel of the leaflet map | `17` |
| Z | maxZoom | max zoomlevel of the leaflet map | if `vectorserverUrl` available, use `17` else `20` |
| A | attribution | attribution legend | `'osm-static-maps / © OpenStreetMap contributors'` |
| t | tileserverUrl | url of a tileserver | `'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'` |
| m | vectorserverUrl | url of a vector tile server (MVT style.json) | `undefined` |
| M | vectorserverToken | token of the vector tile server (MVT) | `'no-token'` |
| D | renderToHtml | returns html of the webpage containing the map (instead of a binary image) | `false` |
| F | type | format of the image returned (`'jpeg'`/`'png'`) | `'png'` |
| q | quality | quality of the image returned (`0`-`100`, only for `jpg`) | `100` |
| x | imagemin | enable lossless compression with [optipng](https://github.com/imagemin/optipng-bin) / [jpegtran](https://github.com/imagemin/jpegtran-bin) | `false` |
| X | oxipng | enable losslsess compression with [oxipng](https://github.com/shssoichiro/oxipng) | `false` |
| C | pngcrush | enable lossless compression with [pngcrush](https://pmt.sourceforge.io/pngcrush/) | `false` |
| j | jpegoptim | enable lossless compression with [jpegoptim](https://github.com/tjko/jpegoptim) | `false` |
| a | arrows | render arrows to show the direction of linestrings | `false` |
| s | scale | enable render a scale ruler (boolean or [a json options object](https://leafletjs.com/reference-1.6.0.html#control-scale-option)) | `false` |
| T | timeout | miliseconds until page load throws timeout | `20000` |
| k | markerIconOptions | set marker icon options ([a json options object](https://leafletjs.com/reference-1.6.0.html#icon-option)) *see note | `undefined` (leaflet's default marker) |
| S | style | style to apply to each feature ([a json options object](https://leafletjs.com/reference-1.6.0.html#path-option)) *see note | `undefined` (leaflet's default) |
<!-- | e | haltOnConsoleError | throw error if there is any `console.error(...)` when rendering the map image | `false` | -->

* Note on markerIconOptions: it's also accepted a markerIconOptions attribute in the geojson feature, for example `{"type":"Point","coordinates":[-105.01621,39.57422],"markerIconOptions":{"iconUrl":"https://leafletjs.com/examples/custom-icons/leaf-red.png"}}`

* Note on style: it's also accepted a pathOptions attribute in the geojson feature, for example `{"type":"Polygon","coordinates":[[[-56.698,-36.413],[-56.716,-36.348],[-56.739,-36.311]]],"pathOptions":{"color":"#FF5555"}}` (also remember that the `#` char needs to be passed as `%23` if you are using GET params)

## LICENSE

 - GPLv2

## Credits

Huge thanks to @jperelli for the nodejs version this was based on.
