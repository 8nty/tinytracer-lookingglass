# TinyTracer

Small looking glass tool using Flask and python3.6+, designed for both IPv4 and IPv6. Only a single device/router is supported per instance at this time.

[![TinyTracer in action](https://lasagna.cat/t/soxovn97k.png)](https://lasagna.cat/i/oxovn97k.png)

## Try it out

I host an instance of this for AS208590 at https://lg.lasagna.dev/

# RFC8522

This code is mostly compliant with [RFC8522 Looking Glass Command Set](https://tools.ietf.org/html/rfc8522), things it lacks include:

- Multiple device (referred to as router in the RFC) support
- Query Parameters
- `.well-known/looking-glass/v1/routers`
- `.well-known/looking-glass/v1/routers/{number}`
- Router field in results

## Running

- **Recommended:** Create a separate user to run tinytracer, give it NOPASSWD sudo permissions to ping, mtr and birdc (Example: `tinytracer ALL=(ALL) NOPASSWD: /usr/bin/mtr,/bin/ping,/usr/sbin/birdc`)
- Install python3.6+ and the dependencies (`pip3 install -Ur requirements.txt`)
- `git clone` this repo
- Copy `config.json.template` to `config.json`
- Configure `config.json` with your information, you can find commands to get inspiration from [here](https://mtr.sh/caps.json)
- Set up the systemd service and nginx (example configs provided in the `runtimeconfigs` folder)
- **If you used something based on example configs:** Run tinytracer with `systemctl start tinytracer`, and reload nginx with `systemctl reload nginx`, and tinytracer should be available on port 80 of the `server_name` you provided. Use something like `certbot` to install certs.
- **If you didn't use something based on example configs:** You're on your own. Things like running the python file directly or using `flask run` *will* work, but `showip` may be broken, and there may be security implications. Good luck.
- Enjoy tinytracer.

## Enabling test files

TinyTracer has no "test files" support built in. You however can add links to them using the info -> blurb section of `config.json`, and serve them using your of choice, and the template has the text for this. TinyTracer does provide scripts and example configs to make this easier.

To generate test files with sizes of 25MB, 50MB and 100MB, go to `testfiles` directory and run `gentestfiles.sh`. You'll need dd.

To "enable" them, just set your reverse proxy to serve the testfiles directory under `/testfiles`, or anywhere else you specify in your blurb. An example for nginx is provided on `runtimeconfigs/nginx-example-tinytracer-withtestfiles.conf`.

## Credits

- This project was developed by Ave Ozkal.
- A lot of example commands were taken from [intrace](https://github.com/Fusl/intrace) ([specifically here](https://github.com/Fusl/intrace/blob/master/config/caps.json.example)).
- A lot of inspiration for the template network information text was taken from [telephone/LookingGlass](https://github.com/telephone/LookingGlass)
- This project is dedicated to [Heather Heyer](https://en.wikipedia.org/wiki/Charlottesville_car_attack#Heather_Heyer). You are not forgotten, you will not be forgotten.
