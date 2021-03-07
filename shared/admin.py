from django.contrib import admin

from .models import Addresses, Contact, ContactContacted, People, TestContacted, Test
# Register your models here.
# TODO: remove these before production (these allow for basic editing/adding of data)
admin.site.register(Addresses)
admin.site.register(Contact)
admin.site.register(ContactContacted)
admin.site.register(People)
admin.site.register(TestContacted)
admin.site.register(Test)
