import argparse
import base64
import csv
import json
import logging
import math
import time

from elasticsearch import Elasticsearch

LOGGER = logging.getLogger('plagiator')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
LOGGER.addHandler(console)


def main(args):
    client = Elasticsearch()
    index = args['es_index']
    if client.indices.exists(index):
        LOGGER.info("Deleteting index {}...", index)
        client.indices.delete(index)
        LOGGER.info("Done")
    with open(args['es_template']) as es_template:
        template = json.load(es_template)
        client.indices.create(index, body=template)

    with open(args['file']) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(reader)
        doc_id = 1
        for row in reader:
            document = {'nom': '', args['column']: ''}
            for idx in range(len(row)):
                if header[idx] == args['column']:
                    document[header[idx]] = row[idx]
                else:
                    document['nom'] = document['nom'] + row[idx]
            result = client.index(index=index, id=doc_id, body=json.JSONEncoder().encode(document))
            doc_id = doc_id + 1
    time.sleep(2)
    LOGGER.info("Indexed " + str(doc_id - 1) + " documents")
    docs = getDocuments(client, index)
    LOGGER.info("Found " + str(len(docs)) + " documents")
    distances = {}
    for i in range(len(docs)):
        for j in range(len(docs)):
            if j != i:
                keys = sorted([docs[i]['name'], docs[j]['name']])
                nameKey = "{}->{}".format(keys[0], keys[1])
                distances[nameKey] = getDistance(docs[i]["value"], docs[j]["value"])

    for k, v in sorted(distances.items(), key=lambda item: item[1]):
        print('{}: {}'.format(k, v))


def getDocuments(client, index, size=1000):
    query = '''
    {
    "size": 1000,
    "_source": ["nom"],
    "stored_fields": ["codeMinhash"],
    "query": {"match_all": {}}
    }
    '''
    result = client.search(index=index, body=query)
    documents = []
    for d in result['hits']['hits']:
        name = d['_source']['nom']
        minhashValues = toVector(d['fields']['codeMinhash'][0])
        documents.append({'name': name, 'value': minhashValues})
    return documents


def toVector(minHashBase64, numBits = 4):
    array = base64.b64decode(minHashBase64)
    offset = 7
    result = []
    for b in array:
        mask = ((1 << numBits) - 1)
        val1 = (b & (mask << 4)) >> 4
        val2 = b & mask
        result.append(val1)
        result.append(val2)
    return result


def getDistance(v1, v2):
    try:
        ss = sum([(x - y) ** 2 for x, y in zip(v1, v2)])
        return math.sqrt(ss)
    except Exception as exception:
        LOGGER.error(exception)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find similar "codes" in given csv column.')
    parser.add_argument('file', help='CSV file to read input from.')
    parser.add_argument('--column', default='Resposta',
                        help='The name of the column to check for similarity')
    parser.add_argument('--es-host', default='localhost',
                        help='es host to connect to')
    parser.add_argument('--es-port', default='9200', type=int,
                        help='es HTTP port')
    parser.add_argument('--es-template', default='template.json',
                        help='Template file for ES index')
    parser.add_argument('--es-index', default='submissions',
                        help='ES index name')
    parser.add_argument('--threshold', default='0.95',
                        help='Threshold for documents similarity')
    main(vars(parser.parse_args()))