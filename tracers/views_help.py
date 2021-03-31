from shared.models import Test, TestContacted
from django.db import transaction
import datetime
from datetime import timezone, timedelta
from django.db.models import Q

# time after which claim expires
expiry_time = timedelta(hours=1)

# for reference, in this datetime representation, future > past


def tests_needing_contacting():
    unexpired_claim = Q(being_contacted__exact=True) & Q(contact_start__gt=datetime.datetime.now(timezone.utc) - expiry_time)
    return Test.objects.exclude(unexpired_claim) \
        .exclude(person__in=TestContacted.objects.values_list('case', flat=True)) \
        .filter(result__exact=True)


# claims & returns earliest positive test that hasn't been claimed
def next_test():
    try:
        with transaction.atomic():
            test = tests_needing_contacting().earliest('test_date')
            test.being_contacted = True
            test.save()
    except Test.DoesNotExist:
        test = None
    return test


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

