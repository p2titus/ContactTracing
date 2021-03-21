"""Hook to call when you add stuff to the database"""
from .dbscan import cluster

def contact_hook(contact):
    """Call this once you have added the contact and location/etc. to the database"""
    cluster(contact)

def test_hook(test):
    # Put stats generation hooks here
    pass



