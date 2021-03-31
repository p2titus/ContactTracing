from django.test import TestCase
from shared.models import *
from .. import views_help

# create database entries from minimal data (preserving order)
def loadToyData(xs):
    # tests currently differentiate people by name only - assert no duplicate names
    assert len(xs) == len(set(map(lambda x: x[0], xs)))

    a = Addresses(addr="", postcode="")
    a.save()
    for psn, res, contacted in xs:
        p = People(name=psn, location=a,
                   phone_num="", email="hello@gmail.com")
        p.save()
        t = Test(person=p, result=res)
        t.save()
        if contacted:
            TestContacted.objects.create(case=t)


def toyExpectedNext(xs):
    # removes & returns expected next element
    # returns None if no uncontacted positive test found
    for i in range(len(xs)):
        x = xs[i]
        if x[1] and not x[2]:
            del xs[i]
            return x
    return None


# testing the most basic functionality
class GetUncontactedTest(TestCase):
    datalist = [("Jane Doe", False, False),
                ("John Doe", True, False),
                ("Joe Bloggs", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_next_is_earliest_pos(self):
        self.assertEqual(views_help.next_test().person.name,
                         toyExpectedNext(self.datalist)[0])


class DontGetContactedTest(TestCase):
    datalist = [("Jane Doe", False, False),
                ("John Doe", False, True),
                ("Joe Bloggs", True, True)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_no_next(self):
        self.assertEqual(views_help.next_test(), toyExpectedNext(self.datalist))

class GetTestsInSequence(TestCase):
    datalist = [("Jane Doe", True, False),
                ("John Doe", True, False),
                ("Joe Bloggs", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_next_is_earliest_pos(self):
        for i in range(3):
            self.assertEqual(views_help.next_test().person.name,
                             toyExpectedNext(self.datalist)[0])
        # should 'run out'
        self.assertEqual(views_help.next_test(),
                         toyExpectedNext(self.datalist))

class ClaimExpires(TestCase):
    datalist = [("Jane Doe", True, False),
                ("John Doe", True, False),
                ("Joe Bloggs", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_claim_expires(self):
        t1 = views_help.next_test()

        # simulate passage of time by manually changing contact_start field to 'a long time in the past'
        t1.contact_start -= views_help.expiry_time * 2
        t1.save(update_fields=["contact_start"])

        t2 = views_help.next_test()
        self.assertEqual(t1, t2)

class ClaimCanBeRefreshed(TestCase):
    datalist = [("Jane Doe", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_claim_refreshed(self):
        t1 = views_help.next_test()
        orig_time = t1.contact_start
        self.assertTrue(views_help.refresh_claim(t1))
        self.assertGreater(t1.contact_start, orig_time)

class ExpiredClaimCantBeRefreshed(TestCase):
    datalist = [("Jane Doe", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_cant_be_refreshed(self):
        t1 = views_help.next_test()

        # simulate passage of time with manual update to contact_start field
        t1.contact_start -= views_help.expiry_time * 2
        t1.save(update_fields=["contact_start"])

        self.assertFalse(views_help.refresh_claim(t1))


# Figure out the "naive datetime" error
#I feel like I haven't explored the issue of time travel/dates in the future
#expiring claims needs to be tested
# change after adding new contacted entries needs to be tested