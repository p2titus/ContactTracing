import pika
import json


# essentially macros
POS_CASE = 'pos_case'
IN_CONTACT = 'in_contact'
PARAM_FILE = 'param.json'
RABBITMQ_STARTUP_SCRIPT = 'start_rabbitmq.sh'
HOSTNAME = None
PORT = 25672


def main():
    params = parse()
    global HOSTNAME
    HOSTNAME = params['host']
    start_server(params)
    chan, con = setup(params=params)
    print('queues created')
    input('press enter to close this connection to rabbit-mq gracefully')
    con.close()


def start_server(params=None):
    if params is None:
        params = {'host': HOSTNAME}
    import socket
    # check to see if server listening on default port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_active = s.connect_ex(params['host'], PORT)
    # start server via bash script if it isn't already running
    if not server_active:
        import subprocess
        subprocess.call(RABBITMQ_STARTUP_SCRIPT)


def setup(params: dict) -> (pika.connection.channel.Channel, str):
    host = params['host']
    con = pika.BlockingConnection(pika.ConnectionParameters(host))
    chan = con.channel()
    chan.queue_declare(queue=POS_CASE, durable=True)
    chan.queue_declare(queue=IN_CONTACT, durable=True)
    return chan, con


def parse():
    global PARAM_FILE
    with open(PARAM_FILE) as f:
        data = json.load(f)
    return data


# used to add positive cases to the queue
def add_poscase(case):
    chan, con = setup()
    chan.basic_publish(exchange='', routing_key=POS_CASE, body=case)


if __name__ == '__main__':
    main()
