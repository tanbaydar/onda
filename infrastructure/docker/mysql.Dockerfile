FROM mysql:8.4@sha256:b3b90af2a6552ae30c266fdb7d5dd55f3afb72404bb78d37fe8a23eb857fd3fb

# Direct non-root startup never invokes the image's privilege-dropping helper.
# Remove it, and the unused MySQL Shell bundle, from production.
RUN microdnf update -y \
    && microdnf clean all \
    && rm -rf /usr/local/bin/gosu /usr/lib/mysqlsh /usr/bin/mysqlsh

# The official entrypoint supports direct non-root startup when the data and
# runtime directories are owned by this account. Compose supplies matching
# tmpfs ownership for the runtime paths below.
USER mysql
