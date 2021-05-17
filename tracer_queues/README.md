the tracer_queues directory is dedicated to providing access to rabbitmq

rabbitmq is used primarily to provide a distributed queue of cases and contacts
to be contacted. whenever a test or a contact is input into the system, it is
saved to the database and pushed to rabbitmq. tracers will then retrieve these
via calls to the queue. this removes all race hazards on the database by
relying on rabbitmq to output each case at most once.

this implementation has a few requirements:
- an instance of rabbitmq-server must already be running on the node (a basic
startup script is left over from earlier in development)
- parameters in main.py must be configured correctly
- relevant queues must be created. this can be done by running 
tracer_queues/main.py independently of the website

additionally, there is some additional setup required:
- this version of rabbitmq currently operates using localhost. likely other
servers will be configured and as such, this class may require rewrites. all
rabbitmq specific functionality is confined to tracer_queues/main.py so changes
should only be local to there
- currently, a distributed database is required. there may be a better solution
not involving one but this was beyond the scope of our project
- the implementation of the tracers section of the website still locks and
writes to databases whenever a contact is accessed. tying in with the previous
point, it may be possible to skip this again.

