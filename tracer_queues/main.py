import datetime

import pika
import json


# essentially macros
POS_CASE = 'pos_case'
IN_CONTACT = 'in_contact'
PARAM_FILE = 'param.json'
RABBITMQ_STARTUP_SCRIPT = './start_rabbitmq.sh'
HOSTNAME = 'localhost'  # default value given for testing
PORT = 25672
PERSISTENT = 2


def run_server_instance():
    params = parse()
    if params is not None:
        global HOSTNAME
        HOSTNAME = params['host']
    start_server(params)
    chan, con = setup(params=params)
    print('queues created')
    input('press enter to close this connection to rabbit-mq gracefully\n')
    con.close()


def start_server(params=None):
    '''if params is None:
        params = {'host': HOSTNAME}
    import socket
    # check to see if server listening on default port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_active = s.connect_ex((params['host'], PORT))
    # start server via bash script if it isn't already running
    if not server_active:
        import subprocess
        subprocess.call(RABBITMQ_STARTUP_SCRIPT)'''
    pass  # TODO - get this working


def setup(params: dict):
    if params is None:
        host = HOSTNAME
    else:
        host = params['host']
    con = pika.BlockingConnection(pika.ConnectionParameters(host))
    chan = con.channel()
    chan.queue_declare(queue=POS_CASE, durable=True)
    chan.queue_declare(queue=IN_CONTACT, durable=True)
    chan.basic_qos(prefetch_count=1)
    return chan, con


def parse():
    import os
    if os.path.isfile(PARAM_FILE):
        with open(PARAM_FILE) as f:
            data = json.load(f)
    else:
        data = None
    return data


# used to add positive cases to the queue
async def add_poscase(case):
    chan, con = setup(None)
    dte = DateTimeEncoder()
    chan.basic_publish(exchange='', routing_key=POS_CASE, body=dte.encode(case),
                       properties=pika.BasicProperties(
                           delivery_mode=PERSISTENT,
                       ))


class DateTimeEncoder(json.JSONEncoder):
    import typing

    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        else:
            json.dumps(o)


def retrieve_pos_case():
    rp = RetrievePerson()
    return rp.retrieve_person(POS_CASE)


def retrieve_contact():
    rp = RetrievePerson()
    return rp.retrieve_person(IN_CONTACT)


class RetrievePerson:
    __response = None

    @staticmethod
    def __date_time_decoder(xs):
        import dateutil

        date_field_name = 'test_date'

        if date_field_name in xs:
            xs[date_field_name] = dateutil.parser.parse(xs[date_field_name])
            return xs

    def retrieve_person(self, chan_name):

        def callback(ch, method, properties, body):
            print('received %r' % body)
            self.__response = json.loads(body, object_hook=self.__date_time_decoder)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        chan, con = setup(None)

        chan.basic_qos(prefetch_count=1)
        chan.basic_consume(queue=chan_name, on_message_callback=callback)
        chan.start_consuming()

        # with these figures, it checks the queue 20 times (once per millisecond) for a total of 20ms then continues
        # this parameter may need to be made longer to allow for more checks
        count = 0
        max = 20
        interval = 0.01  # 0.01s

        while self.__response is None and count < max:
            count += 1
            import time
            time.sleep(interval)

        return self.__response


if __name__ == '__main__':
    run_server_instance()
