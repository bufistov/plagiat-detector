# Find similar documents using MinHash similarity

# RUN

[Docker](https://docs.docker.com/get-docker/) and [python3](https://www.python.org/downloads/) are required to run this program.

####  Build Elasticsearch image

```
docker build -t es-with-minhash ./ 
```

####  Start Elasticsearch

```
./start_es.sh
```

#### Install elasticsearch client library
```
pip install elasticsearch
```
#### List documents sorted by similarity

```
python3 main.py respostes.csv
```

#### To get more help

```
python3 main.py -h
```