import re
import json
import time
from datetime import datetime
import subprocess
from flask import Flask, jsonify, render_template

app = Flask(__name__)
re_ipv4 = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
# Not even gonna bother splitting this into multiple lines
# From https://stackoverflow.com/a/17871737/3286892
# by David M. Syzdek (https://stackoverflow.com/users/903194/david-m-syzdek)
re_ipv6 = re.compile(
    r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
)

with open("config.json") as f:
    config = json.load(f)


def check_ip(ip):
    if re_ipv4.fullmatch(ip):
        return 4
    elif re_ipv6.fullmatch(ip):
        return 6

    return False


@app.route("/")
def serve_static():
    return render_template(
        "index.html", info=config["info"], commands=config["commands"]
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


@app.route("/.well-known/looking-glass/v1/<path:task_name>/<string:ip>")
def do_task(task_name, ip):
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
