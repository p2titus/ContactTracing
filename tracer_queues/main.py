import datetime

import pika
import json


# essentially macros
EXCHANGE_NAME = 'cases'
POS_CASE = 'pos_case'
IN_CONTACT = 'in_contact'
PARAM_FILE = 'param.json'
RABBITMQ_STARTUP_SCRIPT = './start_rabbitmq.sh'
HOSTNAME = 'localhost'  # default value given for testing
PORT = 25672
PERSISTENT = 2

"""
acts as a wrapper around rabbitmq
running the file will create the pre-requisite exchanges needed
"""


# pre: rabbitmq instance required to be running already
# declares the required queues to be used for retrieval and sending of pos cases/contacts to be contacted
def run_server_instance():
    global HOSTNAME

    params = parse(PARAM_FILE)
    HOSTNAME = params['host']
    setup_queues(params)


def setup_queues(params):
    host = params['host']
    con = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    chan = con.channel()

    qs = [POS_CASE, IN_CONTACT]

    for q in qs:
        chan.queue_declare(queue=q, durable=True)

    return con, chan


def parse(param_file):
    try:
        with open(param_file) as f:
            params = json.load(f)
    except IOError:
        params = {'host': HOSTNAME}
    if 'host' not in params:
        params.update({'host': HOSTNAME})

    return params


def __setup(qname):
    con = pika.BlockingConnection(pika.ConnectionParameters(host=HOSTNAME))
    chan = con.channel()
    chan.queue_declare(queue=qname, durable=True)
    return chan, con


# used to add contacts/positive cases to the contact tracing queue
def __add_to_queue(qname, case):
    chan, con = __setup(qname)
    dte = DateTimeEncoder()
    chan.basic_publish(exchange='', routing_key=qname, body=dte.encode(case),
                       properties=pika.BasicProperties(
                           delivery_mode=PERSISTENT,
                       ))
    con.close()


# used to add contacts of positive cases to the queue
def add_contact(contact):
    __add_to_queue(IN_CONTACT, contact)


# used to add positive cases to the queue
def add_poscase(case):
    __add_to_queue(POS_CASE, case)


class DateTimeEncoder(json.JSONEncoder):
    import typing

    def default(self, o: typing.Any) -> typing.Any:
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        else:
            json.dumps(o)


def retrieve_pos_case():
    rp = RetrievePerson()
    chan, con = __setup(POS_CASE)
    return rp.retrieve_person(POS_CASE, chan, con)


def retrieve_contact():
    rp = RetrievePerson()
    chan, con = __setup(IN_CONTACT)
    return rp.retrieve_person(IN_CONTACT, chan, con)


# initially, this used a callback function to write to the instance variable
# however, this can be accomplished much better through use of basic_get
# the class remains, and can probably be refactored to remove the class
# the class is only instantiated in retrieve_pos_case and retrieve_contact
class RetrievePerson:

    @staticmethod
    def __date_time_decoder(xs):
        import dateutil.parser

        date_field_name = 'test_date'

        if date_field_name in xs:
            xs[date_field_name] = dateutil.parser.parse(xs[date_field_name])
            return xs

    def retrieve_person(self, chan_name, chan, con):

        """def callback(ch, method, properties, body):
            print('received %r' % body)
            self.__response = json.loads(body, object_hook=self.__date_time_decoder)
            ch.basic_ack(delivery_tag=method.delivery_tag)"""

        # chan, con = __setup(chan_name)

        status = chan.queue_declare(queue=chan_name, durable=True)

        # we only attempt to retrieve a message if there is a message not awaiting an acknowledgment
        if status.method.message_count > 0:
            method, head, response = chan.basic_get(queue=chan_name)
            decoded = response.decode('utf-8')
            person = json.loads(decoded, object_hook=self.__date_time_decoder)
            chan.basic_ack(delivery_tag=method.delivery_tag)
        # if we cannot find a message, we simply return None
        else:
            person = None

        con.close()

        return person


if __name__ == '__main__':
    run_server_instance()
