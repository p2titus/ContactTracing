from shared.models import Test, TestContacted
from django.db import transaction
import datetime
from datetime import timedelta
from django.db.models import Q


# claims & returns earliest positive test that hasn't been claimed
# a claim will eventually expire
def tests_needing_contacting():
    expiry_time = timedelta(hours=1)
    claim_requirement = Q(being_contacted__exact=True) & Q(contact_start__gt=datetime.datetime.now() - expiry_time)
    return Test.objects.exclude(claim_requirement) \
        .exclude(person__in=TestContacted.objects.values_list('case', flat=True)) \
        .filter(result__exact=True)


def next_test():
    try:
        with transaction.atomic():
            test = tests_needing_contacting().earliest('test_date')
            test.being_contacted = True
            test.save()
    except Test.DoesNotExist:
        test = None
    return test
