FROM mysql:26.7@sha256:66aec17cd21a956029b83f083b813073859e8355dc1a00e55df6ba02f0e32345

# Direct non-root startup never invokes the image's privilege-dropping helper.
# Remove it, and the unused MySQL Shell bundle, from production.
RUN microdnf update -y \
    && microdnf clean all \
    && rm -rf /usr/local/bin/gosu /usr/lib/mysqlsh /usr/bin/mysqlsh

# The official entrypoint supports direct non-root startup when the data and
# runtime directories are owned by this account. Compose supplies matching
# tmpfs ownership for the runtime paths below.
USER mysql
