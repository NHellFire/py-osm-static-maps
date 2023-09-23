from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from base64 import b64encode
from PIL import Image
from io import BytesIO, IOBase
from shutil import which

from jinja2 import Template

from werkzeug.exceptions import BadRequest

import requests

if __package__:
    from .utils import staticFiles, compressimage, get_argparser
else:
    from utils import staticFiles, compressimage, get_argparser


def osmsm(opts, driver=None):
    quit_driver = False

    # Validate argument types
    # We could probably use argparse to do this
    for k,t in {"maxZoom": float, "zoom": float, "width": int, "height": int, "quality": int, "timeout": int}.items():
        if opts.get(k) is not None:
            try:
                opts[k] = t(opts[k])
            except ValueError:
                raise BadRequest(description=f"{k} must be a valid {t.__name__}")

    # Set missing options to defaults
    # We're doing this here and in server.handler
    # So that we can use the command line args as defaults
    # for the webserver, and still set them for the library
    default_opts = vars(get_argparser().parse_args([]))
    for k,v in default_opts.items():
        # Don't apply default zoom when we have geojson data, it'll break fitBounds
        if k == "zoom" and (opts.get("geojsonfile") or opts.get("geojson")):
            continue
        if k not in opts:
            opts[k] = v

    # Fetch external geojson
    if opts.get("geojsonfile"):
        if opts.get("geojson"):
            raise BadRequest(description="Only geojson OR geojsonfile can be specified, not both")

        filename = opts.get("geojsonfile")
        if isinstance(filename, str):
            r = requests.get(filename, timeout=5)
            r.raise_for_status()
            opts["geojson"] = r.text
        elif isinstance(filename, IOBase):
            opts["geojson"] = filename.read()

    if opts.get("maxZoom") is None:
        opts["maxZoom"] = 20 if opts.get("vectorserverUrl") is not None else 17

    if not driver:
        service = webdriver.firefox.service.Service(executable_path=which("geckodriver"))
        options = webdriver.firefox.options.Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(service=service, options=options)
        quit_driver = True

    # Calculate the window size for our desired image resolution
    width, height = driver.execute_script("""
        return [window.outerWidth - document.body.clientWidth + arguments[0],
                window.outerHeight - document.body.clientHeight + arguments[1]];
        """, opts["width"], opts["height"])
    driver.set_window_size(width, height)

    # Render template with jinja
    # Can't use flask.render_template if we're being ran from the library,
    # But we're not using any of the flask variables anyway
    template = Template(staticFiles.get("staticmap"))
    html = template.render(**opts, **staticFiles.files)

    if opts["renderToHtml"]:
        # If we started our own browser, we also need to quit it
        if quit_driver:
            driver.quit()

        return html

    encoded = b64encode(html.encode("utf-8")).decode("ascii")
    driver.get(f"data:text/html;base64,{encoded}")

    # Wait for map to finish loading
    WebDriverWait(driver, opts["timeout"] / 1000).until( lambda x: x.execute_script("""return mapReady;"""))

    # Take screenshot
    screenshot = driver.get_screenshot_as_png()

    # Convert to JPEG if requested
    if opts["type"] == "jpeg":
        with Image.open(BytesIO(screenshot)) as im:
            with BytesIO() as out:
                im.save(out, "JPEG", quality=opts["quality"])
                out.seek(0)
                screenshot = out.read()

    # Compress image if requested
    if opts["imagemin"]:
        if opts["type"] == "jpeg":
            screenshot = compressimage(screenshot, ["jpegtran", "-optimize"])
        elif opts["type"] == "png":
            screenshot = compressimage(screenshot, ["optipng", "-out", "/dev/stdout", "/dev/stdin"])
    elif opts["type"] == "jpeg" and opts["jpegoptim"]:
        screenshot = compressimage(screenshot, ["jpegoptim", "--stdout", "-"])
    elif opts["type"] == "png":
        if opts["oxipng"]:
            screenshot = compressimage(screenshot, ["oxipng", "-"])
        elif opts["pngcrush"]:
            screenshot = compressimage(screenshot, ["pngcrush", "/dev/stdin", "/dev/stdout"])

    # If we started our own browser, we also need to quit it
    if quit_driver:
        driver.quit()

    return screenshot
