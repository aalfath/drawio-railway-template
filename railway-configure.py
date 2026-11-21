#!/usr/bin/env python3
"""Railway tweaks applied on every start, after the image's entrypoint and before Tomcat.

- Tomcat's HTTP connector listens on $PORT; the 8443 HTTPS connector is removed
  (Railway terminates TLS at its edge).
- Optional HTTP basic auth: set both DRAWIO_USERNAME and DRAWIO_PASSWORD on the service.
  /healthz and /robots.txt stay open so Railway's health check passes.
Then it execs the command it was given (catalina.sh run).
"""
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

home = os.environ.get("CATALINA_HOME", "/usr/local/tomcat")
port = os.environ.get("PORT", "8080").strip() or "8080"
if not port.isdigit():
    print(f"railway-configure: PORT '{port}' is not a number, using 8080", flush=True)
    port = "8080"

# --- server.xml: HTTP connector on $PORT, no HTTPS connector ---
server_xml = os.path.join(home, "conf", "server.xml")
tree = ET.parse(server_xml, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
for service in tree.getroot().iter("Service"):
    for conn in list(service.findall("Connector")):
        if conn.get("SSLEnabled", "").lower() == "true" or conn.get("port") == "8443":
            service.remove(conn)
        elif conn.get("protocol", "HTTP/1.1").startswith("HTTP/1.1") or "Http11" in conn.get("protocol", ""):
            conn.set("port", port)
            conn.attrib.pop("redirectPort", None)
tree.write(server_xml, encoding="utf-8", xml_declaration=True)
print(f"railway-configure: Tomcat HTTP connector on port {port}", flush=True)

# --- optional basic auth ---
webinf = os.path.join(home, "webapps", "draw", "WEB-INF")
with open(os.path.join(webinf, "web.xml.orig"), encoding="utf-8") as f:
    web = f.read()

user = os.environ.get("DRAWIO_USERNAME", "")
password = os.environ.get("DRAWIO_PASSWORD", "")
users_xml = os.path.join(home, "conf", "tomcat-users.xml")

if user and password:
    constraint = """
  <security-constraint>
    <web-resource-collection>
      <web-resource-name>open</web-resource-name>
      <url-pattern>/healthz</url-pattern>
      <url-pattern>/robots.txt</url-pattern>
    </web-resource-collection>
  </security-constraint>
  <security-constraint>
    <web-resource-collection>
      <web-resource-name>drawio</web-resource-name>
      <url-pattern>/*</url-pattern>
    </web-resource-collection>
    <auth-constraint>
      <role-name>drawio</role-name>
    </auth-constraint>
  </security-constraint>
  <login-config>
    <auth-method>BASIC</auth-method>
    <realm-name>draw.io</realm-name>
  </login-config>
  <security-role>
    <role-name>drawio</role-name>
  </security-role>
"""
    i = web.rfind("</web-app>")
    web = web[:i] + constraint + web[i:]
    with open(users_xml, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<tomcat-users xmlns="http://tomcat.apache.org/xml" version="1.0">\n'
                '  <role rolename="drawio"/>\n'
                f'  <user username={quoteattr(user)} password={quoteattr(password)} roles="drawio"/>\n'
                '</tomcat-users>\n')
    print("railway-configure: basic auth on (DRAWIO_USERNAME / DRAWIO_PASSWORD)", flush=True)
else:
    with open(users_xml, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<tomcat-users xmlns="http://tomcat.apache.org/xml" version="1.0"/>\n')
    if user or password:
        print("railway-configure: WARNING: set both DRAWIO_USERNAME and DRAWIO_PASSWORD "
              "to turn on basic auth; it stays off", flush=True)
    else:
        print("railway-configure: basic auth off (open editor)", flush=True)

with open(os.path.join(webinf, "web.xml"), "w", encoding="utf-8") as f:
    f.write(web)

if len(sys.argv) < 2:
    sys.argv += ["catalina.sh", "run"]
os.execvp(sys.argv[1], sys.argv[1:])
