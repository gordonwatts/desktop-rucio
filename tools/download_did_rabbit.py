# Listen for a rabbit MQ request and download the requested files.
# Looking at the AST, replace the datasets with the downloaded files (relative to "data").
import adl_func_backend.dataset_resolvers.gridds as gridds
import pika
import sys
import ast
import pickle
from time import sleep
import json
import base64

from src.controllers.globals import datasets, cache_prefix
from src.grid.datasets import DatasetQueryStatus


def process_message(ch, method, properties, body):
    # The body contains the ast, in pickle format.
    # TODO: errors! Errors! Errors!
    info = json.loads(body)
    hash = info['hash']
    a = pickle.loads(base64.b64decode(info['ast']))
    if a is None or not isinstance(a, ast.AST):
        print (f"Body of message wasn't of type AST: {a}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Next, lets look at it and process the files.
    ch.basic_publish(exchange='', routing_key='status_change_state', body=json.dumps({'hash':hash, 'phase':'downloading'}))
    new_ast = gridds.use_executor_dataset_resolver(a, chained_executor=lambda a: a)
    ch.basic_publish(exchange='', routing_key='status_change_state', body=json.dumps({'hash':hash, 'phase':'done_downloading'}))

    # Pickle the converted AST back up, and send it down the line.
    new_info = {
        'hash': hash,
        'ast': base64.b64encode(pickle.dumps(new_ast)).decode(),
    }
    ch.basic_publish(exchange='', routing_key='parse_cpp', body=json.dumps(new_info))

    # We are done with the download and we've sent the message on. Time to ask it so
    # we don't try to do it again.
    ch.basic_ack(delivery_tag=method.delivery_tag)

def download_ds (parsed_url, url:str):
    'Called when we are dealing with a local_ds scheme. We basically sit here and wait'

    status = DatasetQueryStatus.query_queued
    while status == DatasetQueryStatus.query_queued:
        ds_name = parsed_url.netloc
        # TODO: This file// is an illegal URL. It actually should be ///, but EventDataSet can't handle that for now.
        status,files = datasets.download_ds(ds_name, do_download=True, prefix='file:////data/')

        if status == DatasetQueryStatus.does_not_exist:
            # TODO: Clearly this is not acceptable.
            return []
        elif status == DatasetQueryStatus.query_queued:
            # We have to continue to wait a little longer
            pass
        elif status == DatasetQueryStatus.results_valid:
            return files
        else:
            raise BaseException("Do not know what the status means!")
        
        # Ok - lets hang out for a while.
        sleep(5)

def listen_to_queue(rabbit_node:str):
    'Download and pass on datasets as we see them'

    # Config the scanner
    gridds.resolve_callbacks['localds'] = download_ds

    # Connect and setup the queues we will listen to and push once we've done.
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_node))
    channel = connection.channel()
    channel.queue_declare(queue='find_did')
    channel.queue_declare(queue='parse_cpp')

    channel.basic_consume(queue='find_did', on_message_callback=process_message, auto_ack=False)

    # We are setup. Off we go. We'll never come back.
    channel.start_consuming()



if __name__ == '__main__':
    bad_args = len(sys.argv) != 2
    if bad_args:
        print ("Usage: python download_did_rabbit.py <rabbit-mq-node-address>")
    else:
        listen_to_queue (sys.argv[1])
