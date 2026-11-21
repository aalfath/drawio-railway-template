[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/drawio-1?utm_medium=integration&utm_source=button&utm_campaign=drawio)

# draw.io on Railway

One-click [draw.io](https://www.drawio.com) (the diagrams.net editor: flowcharts, UML, network, cloud architecture, org charts, BPMN) on Railway, built from this repo.

**Version:** draw.io **32.7.4**. The service builds `FROM jgraph/drawio:32.7.4@sha256:3e3281733f69416b2b632adad05c9c07d434ebb775e01070d55e9f3247cebe31`, the official image from [jgraph/docker-drawio](https://github.com/jgraph/docker-drawio), pinned by version and digest.

## What you get

| Service | Built from | What it does | Volume |
|---|---|---|---|
| **draw.io** (public) | this repo's `Dockerfile` | The draw.io editor on Tomcat, served on `PORT` behind Railway's HTTPS domain. Health check: `/healthz` | none needed |

draw.io keeps no data on the server. Diagrams are saved where the user chooses: a `.drawio` file on their own device, the browser's storage, or a cloud store (GitHub, GitLab, Google Drive, OneDrive) when that integration is set up. A redeploy or restart loses nothing, so the template has no volume and no database.

What this repo adds to the official image (`railway-start.sh`, `railway-configure.py`):

- Tomcat listens on Railway's `PORT` (8080 by default). The image's HTTPS connector on 8443 and its self-signed keystore (which uses a published default password) are dropped: Railway terminates TLS.
- `DRAWIO_BASE_URL` is set from the service's Railway domain, so embed, viewer and lightbox links point at your deployment.
- `/healthz` answers `ok` for Railway's health check, and `/robots.txt` keeps search engines out.
- Optional HTTP basic auth (below).
- A smaller Java heap (`-Xmx512m`): the server side only serves the editor and a few helpers. The editor uses about 120 MB of RAM.

## Variables

The deploy form asks for nothing.

- `PORT` = `8080`: Tomcat's port; the public domain targets it.

Optional, set them on the service after deploy:

- `DRAWIO_USERNAME` and `DRAWIO_PASSWORD`: set **both** to put the whole editor behind HTTP basic auth (one user). `/healthz` stays open for the health check. Without them, anyone with the URL can use the editor. That is how draw.io itself works, since nothing is stored on the server, but basic auth keeps your instance private.
- `DRAWIO_BASE_URL`: set it to `https://YOUR-DOMAIN` after you add a custom domain.
- Every other variable of the official image still works, for example `DRAWIO_CONFIG` (editor configuration JSON), `DRAWIO_LANG`, and the Google Drive, OneDrive and GitLab integrations (`DRAWIO_GOOGLE_*`, `DRAWIO_MSGRAPH_*`, `DRAWIO_GITLAB_*`). See the [image's README](https://github.com/jgraph/docker-drawio#readme).

## Exporting

*Export as* PNG, JPEG, SVG and HTML render in the browser and work out of the box. *Export as PDF* uses the browser's print dialog. Upstream's separate export server (`jgraph/export-server`) has reached end of life, and the official image no longer uses it, so this template doesn't ship it.

## Updates

Each new draw.io release becomes a commit to `main` here: the pinned version and digest in the `Dockerfile` plus an entry in [CHANGELOG.md](CHANGELOG.md). Railway then shows an "update available" notice on your deployed service, and you choose when to apply it. Nothing is stored on the server, so an update needs no migration.

## Run it locally

```sh
docker build -t drawio-railway .
docker run --rm -p 8080:8080 drawio-railway
# open http://localhost:8080
```

## Licence

draw.io is Apache-2.0 ([jgraph/drawio](https://github.com/jgraph/drawio)). The official image's packaging is GPL-3.0 ([jgraph/docker-drawio](https://github.com/jgraph/docker-drawio)). The wrapper files in this repo are MIT.
