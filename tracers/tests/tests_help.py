from shared.models import *

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
