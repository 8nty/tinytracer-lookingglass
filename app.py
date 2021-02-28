import ipaddress
import json
import time
from datetime import datetime
import subprocess
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

with open("config.json") as f:
    config = json.load(f)


def check_ip(ip):
    try:
        address = ipaddress.ip_address(ip)
        return address.version
    except ValueError:
        return False


def return_origin_ip(request):
    request_remote = request.remote_addr
    request_xrip = request.environ.get("HTTP_X_REAL_IP")
    request_xfwf = request.environ.get("HTTP_X_FORWARDED_FOR")
    request_cfcip = request.environ.get("HTTP_CF_CONNECTING_IP")

    if request_xfwf:
        request_xfwf = request_xfwf.split(",")[0]

    if not config.get("trustproxy", False):
        return request_remote
    else:
        request_proxied_remote = request_remote

        if request_xrip:
            request_proxied_remote = request_xrip

        if request_xfwf and request_xfwf != request_xrip:
            request_proxied_remote = request_xfwf

        if request_cfcip:
            request_proxied_remote = request_cfcip

        return request_proxied_remote


@app.route("/")
def serve_static():
    # Only display IP if it's not disabled in config
    ip = (
        return_origin_ip(request)
        if config.get("showip", True)
        else ""
    )

    # mmm hacky code
    ip = request.args.get("ip", ip)
    first_command = list(config["commands"].keys())[0]
    checked_cmd = request.args.get("cmd", first_command)

    return render_template(
        "index.html",
        info=config["info"],
        commands=config["commands"],
        ip=ip,
        checked_cmd=checked_cmd,
    )


@app.route("/.well-known/looking-glass/v1/cmd")
def list_commands():
    output = {"status": "success", "data": {"commands": []}}
    for command in list(config["commands"].keys()):
        href_url = (
            f"{config['host']}/.well-known/looking-glass/v1/{command.replace(' ', '/')}"
        )

        output["data"]["commands"].append(
            {
                "href": href_url,
                "arguments": "{addr}",
                "description": config["commands"][command]["description"],
                "command": command,
            }
        )
    return jsonify(output)


@app.route("/api/capabilities")
def list_capabilities():
    return jsonify(config["capabilities"])


@app.route("/api/info")
def list_info():
    return jsonify(config["info"])


@app.route("/.well-known/looking-glass/v1/<path:task_name>/")
@app.route("/.well-known/looking-glass/v1/<path:task_name>/<string:ip>")
def do_task(task_name, ip=None):
    # Check IP protocol and if it's invalid or not
    ip_type = check_ip(ip)
    if not ip_type:
        response = {"status": "error", "message": "Invalid IP address"}
        return jsonify(response), 400

    # Convert slashes in command names to spaces for multi word stuff (for RFC8522 compliance)
    task_name = task_name.replace("/", " ")

    # Check if command exists or not
    if task_name not in config["commands"]:
        response = {"status": "error", "message": "No such command found"}
        return jsonify(response), 404

    # Check if command supports this protocol
    if f"cmd{ip_type}" not in config["commands"][task_name]:
        response = {
            "status": "error",
            "message": f"This command doesn't support IPv{ip_type}",
        }
        return jsonify(response), 400

    # Check if server supports this protocol
    if not config["capabilities"][f"ipv{ip_type}"]:
        response = {
            "status": "error",
            "message": f"This server doesn't support IPv{ip_type}",
        }
        return jsonify(response), 502

    # Prepare and run the command
    cmd = config["commands"][task_name][f"cmd{ip_type}"].replace("{{TARGET}}", ip)

    start_time = time.monotonic()
    cmd_out = subprocess.run(cmd, shell=True, capture_output=True)
    end_time = time.monotonic()
    end_str = datetime.isoformat(datetime.utcnow())

    # Return stderr if stdout is empty
    if not cmd_out.stdout:
        response = {
            "status": "fail",
            "data": {
                "output": cmd_out.stderr.decode().split("\n"),
                "format": "text/plain",
                "performed_at": end_str,
                "runtime": end_time - start_time,
            },
        }
        return jsonify(response)

    # Return stdout with a success
    response = {
        "status": "success",
        "data": {
            "output": cmd_out.stdout.decode().split("\n"),
            "format": "text/plain",
            "performed_at": end_str,
            "runtime": end_time - start_time,
        },
    }
    return jsonify(response)


if __name__ == "__main__":
    app.debug = config["debug"]
    app.run(host="0.0.0.0")
