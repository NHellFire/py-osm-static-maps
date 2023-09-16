import traceback

from flask import Flask, request, make_response
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import threading
import queue

if __package__:
    from .lib import osmsm
    from .WebdriverPool import WebdriverPool
else:
    from lib import osmsm
    from WebdriverPool import WebdriverPool


app = Flask(__name__)

pool = None
default_opts = {}

def serve(args):
    global pool
    global default_opts

    # Store a copy for use when missing from the request
    default_opts = vars(args)

    options = FirefoxOptions()
    options.add_argument("--headless")
    pool = WebdriverPool(timeout=args.timeout / 1000, webdriver_args={"options": options}, workers=4)

    app.run(host="0.0.0.0", port=args.port, use_reloader=False)

@app.route("/")
def handler():
    global pool

    opts = request.data if request.method == "POST" else request.args
    opts = opts.to_dict()

    filename = opts.get("f", opts.get("geojsonfile", None))
    if filename and not filename.startswith("http://") and not filename.startswith("https://"):
        return "'geojsonfile' parameter must be a URL", 400

    # Set missing options to defaults
    for k,v in default_opts.items():
        if k not in opts:
            opts[k] = v

    resp = make_response()
    driver = None
    try:
        driver = pool.acquire()
        resp.data = osmsm(opts, driver)

        if not opts["renderToHtml"]:
          if opts["type"] == "jpeg":
            resp.content_type = "image/jpeg"
          elif opts["type"] == "png":
            resp.content_type = "image/png"
    except queue.Empty:
        resp = make_response("No free workers", 503)
    except TimeoutException:
        resp = make_response("Timeout", 503)
    except Exception as e:
        traceback.print_exc()
        resp = make_response("Internal error", 500)

    if driver:
        pool.release(driver)

    return resp

@app.route("/health")
def health():
    return "OK"

@app.route("/dynamic")
def dynamic():
    opts = request.data if request.method == "POST" else request.args
    opts = opts.to_dict()
    return "Yay"