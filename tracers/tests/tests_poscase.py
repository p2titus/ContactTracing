from django.test import TestCase
from shared.models import *


# create database entries from minimal data (preserving order)
def loadToyData(xs):
    #tests currently id people by name only - assert no duplicate names
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
        self.assertEqual(Test().get_next().person.name,
                         toyExpectedNext(self.datalist)[0])


class DontGetContactedTest(TestCase):
    datalist = [("Jane Doe", False, False),
                ("John Doe", False, True),
                ("Joe Bloggs", True, True)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_no_next(self):
        self.assertEqual(Test().get_next(), toyExpectedNext(self.datalist))

class GetTestsInSequence(TestCase):
    datalist = [("Jane Doe", True, False),
                ("John Doe", True, False),
                ("Joe Bloggs", True, False)]

    def setUp(self):
        loadToyData(self.datalist)

    def test_next_is_earliest_pos(self):
        for i in range(3):
            self.assertEqual(Test().get_next().person.name,
                             toyExpectedNext(self.datalist)[0])
        #should 'run out'
        self.assertEqual(Test().get_next(),
                         toyExpectedNext(self.datalist))

# change after adding new contacted entries needs to be tested
# concurrency stuff needs to be tested
