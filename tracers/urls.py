"""ContactTracing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Homepage, such as it is:
    path('', views.index, name="index"),

    #pages for displaying cases
    path('poscase/', views.poscase, name="poscase"),
    path('contact/', views.contact, name="contact"),
    path('add_contact/', views.add_contact, name='add_contact'),
    path('add_testcontacted/', views.add_testcontacted, name='add_testcontacted'),
    path('add_contactcontacted/', views.add_contactcontacted, name='add_contactcontacted'),

]
