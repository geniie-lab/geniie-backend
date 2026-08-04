# Installing OpenSearch

See [https://hub.docker.com/r/opensearchproject/opensearch](https://hub.docker.com/r/opensearchproject/opensearch)

We manage the OpenSearch container with a script, `indexing/opensearch/start_opensearch.sh`,
instead of running `docker run` by hand. The script recreates the container from a pinned
image, installs the required analysis plugins, and (optionally) sets up snapshot support
for backups. It is safe to re-run at any time: index data lives in a bind-mounted host
folder and survives container recreation.

## Preparation

1. **A local folder to store index files**, e.g. `/data/opensearch` — passed to the
   script as its argument. The folder must already exist (the script refuses to run
   against a missing path, to avoid silently starting with an empty index).

2. **A `.env` file at the repo root** containing the admin password:

   ```bash
   OPENSEARCH_INITIAL_ADMIN_PASSWORD="[strong password]"
   ```

3. **Check the pinned image version.** The `IMAGE` variable at the top of the script
   must match the OpenSearch version that created your data (Example:
   `opensearchproject/opensearch:3.5.0`). 

## Starting OpenSearch

Run from the **repo root** (the script locates `.env` there):

```bash
# Normal start (no snapshot support)
bash indexing/opensearch/start_opensearch.sh /data/opensearch

# With snapshot support — required before nightly backups can run
bash indexing/opensearch/start_opensearch.sh /data/opensearch --snapshot
```


## Test the connection

```bash
curl https://localhost:9200 -k -u "admin:[strong password]"
# {
#   "name" : "c626c8732069",
#   "cluster_name" : "docker-cluster",
#   ...
#   "version" : {
#     "distribution" : "opensearch",
#     "number" : "3.5.0",
#     ...
#   },
#   "tagline" : "The OpenSearch Project: https://opensearch.org/"
# }
```

Also confirm the indices are healthy (green/yellow, not red):

```bash
curl -sk -u "admin:[strong password]" "https://localhost:9200/_cat/indices?v"
```

## For local testing without a password

The script always runs with security enabled. For a throwaway local test where you want
to skip the admin password, start a container manually instead
(`DISABLE_SECURITY_PLUGIN=true` is for local testing only — never for the instance
holding real indices):

```bash
docker run -d -p 9200:9200 -p 9600:9600 \
    -v [path to local folder]:/usr/share/opensearch/data \
    -e "discovery.type=single-node" \
    -e "DISABLE_SECURITY_PLUGIN=true" \
    -e "DISABLE_INSTALL_DEMO_CONFIG=true" \
    -e "OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g" \
    --add-host=host.docker.internal:host-gateway \
    --name opensearch-node opensearchproject/opensearch:latest
```

Test:

```bash
curl http://localhost:9200
```

Note: use a *different* data folder for such tests, and remove the container afterward —
the managed instance should always be (re)started via `start_opensearch.sh`.

## (Optional) How to create a snapshot manually

```bash
curl -sk -u "admin:[strong password]" -X PUT \
  "https://localhost:9200/_snapshot/local_backup/manual-$(date +%Y%m%d-%H%M)?wait_for_completion=true" \
  -H 'Content-Type: application/json' \
  -d '{ "indices": "*", "include_global_state": true }'
```

To list existing snapshots

```bash
curl -sk -u "admin:[strong password]" "https://localhost:9200/_cat/snapshots/local_backup?v"
```