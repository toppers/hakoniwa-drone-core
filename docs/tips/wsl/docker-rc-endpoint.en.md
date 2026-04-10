[Japanese](docker-rc-endpoint.md) | English

# TIPS

## Using RC Endpoint with WSL2/Docker + Windows Gamepad

This document explains the integrated setup where:

- the simulator runs inside Docker on WSL2/Ubuntu
- `drone service` and `web bridge` run inside the container
- gamepad input runs on Windows via `rc-endpoint.py`
- the whole flow is started from a WSL2 launcher

Prerequisite:

- clone `hakoniwa-drone-core` and `hakoniwa-pdu-endpoint` side by side before following this procedure

Example:

```bash
cd /home/<user>/project
git clone https://github.com/toppers/hakoniwa-drone-core.git
git clone https://github.com/hakoniwalab/hakoniwa-pdu-endpoint.git
```

See the Japanese page for the current full procedure:

- [docker-rc-endpoint.md](docker-rc-endpoint.md)
