# draw.io for Railway: the official jgraph/drawio image, pinned by version and digest,
# plus a small start wrapper (Railway PORT, public URL, optional basic auth, health path).
FROM jgraph/drawio:32.7.4@sha256:3e3281733f69416b2b632adad05c9c07d434ebb775e01070d55e9f3247cebe31

USER root
COPY railway-start.sh railway-configure.py /usr/local/bin/
RUN chmod 755 /usr/local/bin/railway-start.sh /usr/local/bin/railway-configure.py && \
    cd "$CATALINA_HOME/webapps/draw" && \
    cp WEB-INF/web.xml WEB-INF/web.xml.orig && \
    printf 'ok\n' > healthz && \
    printf 'User-agent: *\nDisallow: /\n' > robots.txt && \
    chown tomcat:0 WEB-INF/web.xml WEB-INF/web.xml.orig healthz robots.txt && \
    chmod g=u WEB-INF/web.xml WEB-INF/web.xml.orig healthz robots.txt
USER tomcat

ENTRYPOINT ["/usr/local/bin/railway-start.sh"]
CMD ["catalina.sh", "run"]
