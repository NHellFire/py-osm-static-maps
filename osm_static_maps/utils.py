from base64 import b64encode
from pkg_resources import resource_stream

import argparse
import subprocess


def compressimage(im, cmdline):
    with subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        outs, errs = proc.communicate(input=im)
        im = outs

    return im

def get_argparser():
    parser = argparse.ArgumentParser(
        prog="osmsm",
        description="Generate an image of a geojson with a background map layer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )

    parser.add_argument("-h", "--help", help="show this help message and exit", action="store_true", default=argparse.SUPPRESS)
    parser.add_argument("-g", "--geojson", help="geojson object to be rendered", action="store", default=argparse.SUPPRESS)
    parser.add_argument("-f", "--geojsonfile", help="Geojson file to be rendered (\"-\" reads STDIN)", action="store", type=argparse.FileType("r"), default=argparse.SUPPRESS)
    parser.add_argument("-H", "--height", help="Height in pixels of the rendered image", action="store", default=600, type=int)
    parser.add_argument("-W", "--width", help="Width in pixels of the rendered image", action="store", default=800, type=int)
    parser.add_argument("-c", "--center", help="Center of the map (default: center of geojson or \"-57.9524339,-34.921779\")", action="store", default=argparse.SUPPRESS)
    parser.add_argument("-Z", "--maxZoom", help="Maximum zoomlevel of the map", action="store", type=float, default=17)
    parser.add_argument("-z", "--zoom", help="Zoomlevel of the map (default: vectorserverUrl ? 12 : 20)", action="store", type=float, default=argparse.SUPPRESS)
    parser.add_argument("-A", "--attribution", help="Attribution watermark text", action="store", default="osm-static-maps / © OpenStreetMap contributors")
    parser.add_argument("-t", "--tileserverUrl", help="URL of a tileserver", action="store", default="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    parser.add_argument("-m", "--vectorserverUrl", help="URL of a vector tileserver (MBT style.json)", action="store", default=argparse.SUPPRESS)
    parser.add_argument("-M", "--vectorserverToken", help="Token of the vector tile server (MVT)", action="store", default="no-token")
    parser.add_argument("-D", "--renderToHtml", help="Returns html of the webpage containing the leaflet map (instead of a binary image)", action="store_true", default=False)
    parser.add_argument("-F", "--type", help="Format of the image returned", action="store", default="png", choices=["jpeg", "png"])
    parser.add_argument("-q", "--quality", help="Quality of the image returned (only for -F=jpeg)", action="store", type=int, default=100)
    parser.add_argument("-x", "--imagemin", help="Apply lossless compression with optipng/jpegtran", action="store_true")
    parser.add_argument("-X", "--oxipng", help="Apply lossless compression with oxipng (only for -F=png)", action="store_true")
    parser.add_argument("-C", "--pngcrush", help="Apply lossless compression with pngcrush (only for -F=png)", action="store_true")
    parser.add_argument("-j", "--jpegoptim", help="Apply lossless compression with jpegoptim (only for -F=jpeg)", action="store_true")
    parser.add_argument("-a", "--arrows", help="Render arrows to show the direction of linestrings", action="store_true")
    parser.add_argument("-s", "--scale", help="Enable render a scale ruler (see options in https://leafletjs.com/reference.html#control-scale-option)", action="store_true")
    parser.add_argument("-k", "--markerIconOptions", help="Set marker icon options (see doc in https://leafletjs.com/reference.html#icon-option)", action="store")
    parser.add_argument("-T", "--timeout", help="Miliseconds until page load throws timeout", type=int, action="store", default=20000)
    parser.add_argument("-S", "--style", help="Set path style options (see doc in https://leafletjs.com/reference.html#path-option)", action="store")
# Currently not implemented, selenium doesn't have events for console messages
#    parser.add_argument("-e", "--haltOnConsoleError", help="throw error if there is any console.error(...) when rendering the map image", action="store_true")

    subparser = parser.add_subparsers(dest="command", help=argparse.SUPPRESS)
    serveparser = subparser.add_parser("serve", help="Run as web server", usage=argparse.SUPPRESS, add_help=False)
    serveparser.add_argument("-h", "--help", help=argparse.SUPPRESS, action="store_true")
    serveparser.add_argument("-p", "--port", help="Port number to listen on", action="store", default=3000, type=int)

    return parser


# Singleton to keep a single copy of all our static files in RAM
class StaticFiles(object):
    _instance = None
    _files = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(cls.__class__, cls).__new__(cls)

        return cls._instance

    def load(self, name, file, b64=False):
        if __package__:
            fp = resource_stream(__package__, file)
        else:
            fp = open(file, "rb")
        with fp:
            data = fp.read()
            if b64:
                data = b64encode(data).decode("ascii")
            else:
                data = data.decode("utf-8")
            self.files[name] = data

    def get(self, name):
        return self._files[name]

    @property
    def files(self):
        return self._files;



staticFiles = StaticFiles()
staticFiles.load("staticmap", "templates/staticmap.html")
staticFiles.load("leafletjs", "static/leaflet.min.js")
staticFiles.load("leafletcss", "static/leaflet.min.css")
staticFiles.load("mapboxcss", "static/mapbox-gl.css")
staticFiles.load("mapboxjs", "static/mapbox-gl.js")
staticFiles.load("leafletpolylinedecorator", "static/leaflet.polylineDecorator.js")
staticFiles.load("markericonpng", "static/images/marker-icon.png", True)
staticFiles.load("leafletmapboxjs", "static/leaflet-mapbox-gl.min.js")
