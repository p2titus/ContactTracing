from shared.models import *
from django.db import transaction
import datetime
from datetime import timezone, timedelta
from django.db.models import Q

# time after which claim expires
expiry_time = timedelta(hours=1)
# condition for a person to be claimed (ie should be filtered out)
unexpired_claim = Q(being_contacted__exact=True) \
                  & Q(contact_start__gt=datetime.datetime.now(timezone.utc) - expiry_time)


# for reference, in this datetime representation, future > past


def tests_needing_contacting():
    return Test.objects.exclude(unexpired_claim) \
        .exclude(person__in=TestContacted.objects.values_list('case', flat=True)) \
        .filter(result__exact=True)


# given a dict with the data communicated via rabbitmq, retrieves the corresponding test from the database
def __get_test(td: dict):  # td = test_data
    return Test.objects.filter(person__name=td['name'], person__date_of_birth=td['date_of_birth'],
                               person__phone_num=td['phone_num']).first()
    # the likelihood of two people having the same name, date of birth and phone number is minimal
    # however, if you want a unique entry, you should send more fields via rabbitmq

# claims & returns
# as rabbitmq takes care of race conditions on the database, we are free to read without regard for other processes
# we need to read for the forms this returns to
def next_test():
    import tracer_queues
    next_details = tracer_queues.retrieve_pos_case()
    if next_details is not None:
        try:
            with transaction.atomic():
                now = datetime.datetime.now(timezone.utc)
                test = __get_test(next_details)
                # test = tests_needing_contacting().earliest('test_date')  # originally queried all from one single db
                test.being_contacted = True
                test.contact_start = now
                test.save()
        except Test.DoesNotExist:
            test = None
    else:
        test = None
    return test


# note that a person is filtered out after being contacted
# by a tracer just once.
# over a longer time period, a person would need to be
# contacted twice if entered twice
# TODO: add this feature
def contacts_needing_contacting():
    return Contact.objects.exclude(unexpired_claim) \
        .exclude(case_contact__in=ContactContacted.objects.values_list('contact', flat=True))


def __get_contact(cd: dict):  # cd = contact data
    return Contact.objects.filter(person__name=cd['name'], person__date_of_birth=cd['date_of_birth'],
                                  person__phone_num=cd['phone_num']).first()

# claims & returns
# TODO - check rabbitmq used correctly
def next_contact():
    import tracer_queues
    next_details = tracer_queues.retrieve_contact()
    if next_details is not None:
        try:
            with transaction.atomic():
                now = datetime.datetime.now(timezone.utc)
                contact = __get_contact(next_details)
                # contact = contacts_needing_contacting().first()
                if contact is not None:
                    contact.being_contacted = True
                    contact.contact_start = now
                    contact.save()
        except Contact.DoesNotExist:
            contact = None
    else:
        contact = None
    return contact


# updates timestamp on (un-expired) claim so it doesn't expire
# returns true for successful update
def refresh_claim(psn):
    with transaction.atomic():
        now = datetime.datetime.now(timezone.utc)
        if psn.being_contacted & (psn.contact_start > now - expiry_time):
            psn.contact_start = now
            psn.save(update_fields=["contact_start"])
            return True
        else:
            return False
