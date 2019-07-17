from flask import Flask, jsonify
import subprocess
import json

app = Flask(__name__)

with open("config.json") as f:
    config = json.load(f)


def check_ip(ip):
    # TODO: do actual regexes here
    return True


@app.route('/api/task/<string:task_name>/<string:ip>')
def do_mtr(task_name, ip):
    print(f"IP: {ip}")
    if task_name not in config["tasks"]:
        response = {"success": False, "reason": "No such task found"}
        return jsonify(response)
    # mtr -6zboLDRSNBAWVGJMXI -a 2a0d:1a40:7700:: -rwc10 -i 0.2 -m 50 2a0d:1a40:1337::
    # traceroute -A -q5 -w 2 -6 -m 50 2a0d:1a40:1337::
    # ping6 -c 10 -i 0.2 -t 255  2a0d:1a40:1337::
    subprocess.run(# the command)
        # return output here
    response = {"success": True}
    return jsonify(response)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
