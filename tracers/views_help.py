from shared.models import *
from django.db import transaction
import datetime
from datetime import timezone, timedelta
from django.db.models import Q

# time after which claim expires
expiry_time = timedelta(hours=1)
# condition for a person to be claimed (ie should be filtered out)
unexpired_claim = Q(being_contacted__exact=True) & Q(contact_start__gt=datetime.datetime.now(timezone.utc) - expiry_time)


# for reference, in this datetime representation, future > past


def tests_needing_contacting():
    return Test.objects.exclude(unexpired_claim) \
        .exclude(person__in=TestContacted.objects.values_list('case', flat=True)) \
        .filter(result_poscontact_exact=True)


# claims & returns
def next_test():
    try:
        with transaction.atomic():
            test = tests_needing_contacting().earliest('test_date')
            test.being_contacted = True
            test.save()
    except Test.DoesNotExist:
        test = None
    return test


def contacts_needing_contacting():
    return Contact.objects.exclude(unexpired_claim) \
        .exclude(person__in=ContactContacted.objects.values_list('case', flat=True))


# claims & returns
def next_contact():
    try:
        with transaction.atomic():
            contact = contacts_needing_contacting().earliest('test_date')
            contact.being_contacted = True
            contact.save()
    except Test.DoesNotExist:
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

