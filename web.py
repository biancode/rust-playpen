#!/usr/bin/env python3

import functools
import os
import sys

from bottle import get, request, response, route, run, static_file
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import GasLexer, LlvmLexer

import playpen

@get("/")
def serve_index():
    response = static_file("web.html", root="static")

    # XSS protection is a misfeature unleashed upon the world by Internet
    # Explorer 8. It uses ill conceived heuristics to block or mangle HTTP
    # requests in an attempt to prevent cross-site scripting exploits. It's yet
    # another idea from the "enumerating badness" school of security theater.
    #
    # Rust and JavaScript are both languages using a C style syntax, and GET
    # queries containing Rust snippets end up being classified as cross-site
    # scripting attacks. Luckily, there's a header for turning off this bug.
    response.set_header("X-XSS-Protection", "0")

    return response

@get("/<path:path>")
def serve_static(path):
    return static_file(path, root="static")

@functools.lru_cache(maxsize=256)
def execute(version, command, arguments):
    print("running:", version, command, arguments, file=sys.stderr, flush=True)
    return playpen.execute(version, command, arguments)

def enable_post_cors(wrappee):
    def wrapper(*args, **kwargs):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type"

        if request.method != "OPTIONS":
            return wrappee(*args, **kwargs)

    return wrapper

@route("/evaluate.json", method=["POST", "OPTIONS"])
@enable_post_cors
def evaluate():
    version = request.json["version"]
    if version not in ("master", "0.10"):
        return {"error": "invalid version"}
    optimize = request.json["optimize"]
    if optimize not in ("0", "1", "2", "3"):
        return {"error": "invalid optimization level"}
    out, _ = execute(version, "/usr/local/bin/evaluate.sh", (optimize, request.json["code"]))
    return {"result": out}

@route("/format.json", method=["POST", "OPTIONS"])
@enable_post_cors
def format():
    version = request.json["version"]
    if version not in ("master", "0.10"):
        return {"error": "invalid version"}
    out, rc = execute(version, "/usr/local/bin/format.sh", (request.json["code"],))
    if rc:
        return {"error": out}
    else:
        return {"result": out[:-1]}

@route("/compile.json", method=["POST", "OPTIONS"])
@enable_post_cors
def compile():
    version = request.json["version"]
    if version not in ("master", "0.10"):
        return {"error": "invalid version"}
    emit = request.json["emit"]
    if emit not in ("asm", "ir"):
        return {"error": "invalid emission type"}
    optimize = request.json["optimize"]
    if optimize not in ("0", "1", "2", "3"):
        return {"error": "invalid optimization level"}
    out, rc = execute(version, "/usr/local/bin/compile.sh", (optimize, emit, request.json["code"]))
    if rc:
        return {"error": out}
    else:
        if request.json.get("highlight") is not True:
            return {"result": out}
        if emit == "asm":
            return {"result": highlight(out, GasLexer(), HtmlFormatter(nowrap=True))}
        return {"result": highlight(out, LlvmLexer(), HtmlFormatter(nowrap=True))}

os.chdir(sys.path[0])
run(host='0.0.0.0', port=80, server='cherrypy')
