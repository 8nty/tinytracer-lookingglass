from flask import Flask, jsonify
import subprocess
import json

app = Flask(__name__)

with open("config.json") as f:
    config = json.load(f)


def check_ip(ip):
    # TODO: do actual regexes here
    if "." in ip:
        return 4
    elif ":" in ip:
        return 6
    else:
        return False


@app.route('/api/task/<string:task_name>/<string:ip>')
def do_mtr(task_name, ip):
    ip_type = check_ip(ip)

    if not ip_type:
        response = {"success": False, "reason": "Invalid IP address"}
        return jsonify(response)

    if task_name not in config["tasks"]:
        response = {"success": False, "reason": "No such task found"}
        return jsonify(response)
    
    if f"cmd{ip_type}" not in config["tasks"][task_name]:
        response = {"success": False,
                    "reason": f"This task doesn't support IPv{ip_type}"}
        return jsonify(response)
    
    if not config["capabilities"][f"ipv{ip_type}"]:
        response = {"success": False,
                    "reason": f"This server doesn't support IPv{ip_type}"}
        return jsonify(response)

    cmd = config["tasks"][task_name][f"cmd{ip_type}"].replace("{{TARGET}}", ip)
    cmd_out = subprocess.run(cmd, shell=True, capture_output=True)
    response = {"success": True, "result": cmd_out.stdout.decode()}
    return jsonify(response)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
