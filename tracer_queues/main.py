import pika
import json


# essentially macros
POS_CASE = 'pos_case'
IN_CONTACT = 'in_contact'
PARAM_FILE = 'param.json'


def main():
    params = parse()
    chan, con = setup(params)


def setup(params: dict) -> (pika.connection.channel.Channel, str):
    global POS_CASE
    global IN_CONTACT
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


if __name__ == '__main__':
    main()
