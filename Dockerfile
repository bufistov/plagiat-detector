#!/bin/sh
FROM docker.elastic.co/elasticsearch/elasticsearch:7.6.0

RUN ./bin/elasticsearch-plugin install org.codelibs:elasticsearch-minhash:7.6.0
