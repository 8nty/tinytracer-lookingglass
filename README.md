# TinyTracer

Small looking glass tool using Flask and python3.6+, designed for both IPv4 and IPv6. Only a single device is supported at this time.

Configuration is done through `config.json`, the `commands` section is compatible with `caps.json` capabilities from mtr.sh/intrace.

This code is mostly compliant with [RFC8522 Looking Glass Command Set](https://tools.ietf.org/html/rfc8522), things it lacks include:

- Multiple device (referred to as router in the RFC) support
- Query Parameters
- `.well-known/looking-glass/v1/routers`
- `.well-known/looking-glass/v1/routers/{number}`
- Router field in results

## Try it out

I host an instance of this for AS208590 at https://lg.lasagna.dev/

## Running

- **Recommended:** Create a separate user to run tinytracer, give it NOPASSWD sudo permissions to ping, mtr and birdc (Example: `tinytracer ALL=(ALL) NOPASSWD: /usr/bin/mtr,/bin/ping,/usr/sbin/birdc`)
- Install python3.6+ and the dependencies (`pip3 install -Ur requirements.txt`)
- `git clone` this repo
- Copy `config.json.template` to `config.json`
- Configure `config.json` with your information, you can find commands to get inspiration from [here](https://mtr.sh/caps.json)
- Set up the systemd service and nginx (example configs provided in the `runtimeconfigs` folder)
- **If you used something based on example configs:** Run tinytracer with `systemctl start tinytracer`, and reload nginx with `systemctl reload nginx`, and tinytracer should be available on port 80 of the `server_name` you provided. Use something like `certbot` to install certs, and enjoy tinytracer.
- **If you didn't use something based on example configs:** You're on your own. Things like running the python file directly or using `flask run` *will* work, but `showip` may be broken, and there may be security implications. Good luck.

## Dedicated to

This project is dedicated to Heather Heyer. You are not forgotten, you will not be forgotten.

