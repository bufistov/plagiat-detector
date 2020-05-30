#!/bin/bash

docker run -p 9200:9200 -p 9300:9300 \
-e "discovery.type=single-node" \
-e "ES_JAVA_OPTS=-Xms256m -Xmx256m" \
-e "network.publish_host=127.0.0.1" \
-e "xpack.security.enabled=false" es-with-minhash:latest
