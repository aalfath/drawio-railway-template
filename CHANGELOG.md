# Changelog

Breaking changes come first in each entry.

## 32.7.4 (2026-11-21)

First release of the template.

- draw.io 32.7.4 on the official image `jgraph/drawio:32.7.4@sha256:3e3281733f69416b2b632adad05c9c07d434ebb775e01070d55e9f3247cebe31`.
- Tomcat listens on Railway's `PORT`. The HTTPS connector and its default-password keystore are removed, because Railway terminates TLS.
- `DRAWIO_BASE_URL` comes from the Railway domain. `/healthz` serves the health check, and `/robots.txt` disallows indexing.
- Optional HTTP basic auth through `DRAWIO_USERNAME` and `DRAWIO_PASSWORD`.
