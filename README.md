# TinyTracer

Small looking glass tool using flask and python3.6+, designed for both IPv4 and IPv6. Only a single device is supported at this time.

Configuration is done through `config.json`, the `commands` section is compatible with `caps.json` capabilities from mtr.sh/intrace.

This code is mostly compliant with [RFC8522 Looking Glass Command Set](https://tools.ietf.org/html/rfc8522), things it lacks include:

- Multiple device (referred to as router in the RFC) support
- Query Parameters (planned to be supported)
- `.well-known/looking-glass/v1/routers` (planned to be supported)
- `.well-known/looking-glass/v1/routers/{number}` (planned to be supported)
- Router field in results (planned to be supported)

## Try it out

I host an instance of this for AS208590 at https://lg.lasagna.dev/

## Dedicated to

This project is dedicated to Heather Heyer. You are not forgotten, you will not be forgotten.

