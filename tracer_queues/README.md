The tracer_queues directory is dedicated to providing and encapsulating access 
to rabbitmq

RabbitMQ is used primarily to provide a distributed queue of cases and contacts
to be contacted. Whenever a test or a contact is input into the system, it is
saved to the database and pushed to rabbitmq. tracers will then retrieve these
via calls to the queue. This removes all race hazards on the database by
relying on rabbitmq to output each case at most once.

This implementation has a few requirements:
- An instance of rabbitmq-server must already be running on the node (a basic
startup script is left over from earlier in development)
- Parameters in main.py must be configured correctly
- Relevant queues must be created. this can be done by running 
tracer_queues/main.py independently of the website

Additionally, there is some additional setup required:
- As the structure of the website server was not known, this implementation
operates entirely by localhost. In practice, this should be configured in a way
that works best with the project.
- Currently, a distributed database is required. There may be a better solution
not involving a distributed database but this was beyond the scope of our project
- The implementation of the tracers section of the website still locks and
writes to databases whenever a contact is accessed. Tying in with the previous
point, it may be possible to skip this again.

