from django.urls import include

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
from django.views.generic.base import TemplateView

urlpatterns = [

    # redirects to login view - this should handle business logic of whether user is already logged in or not
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # everything related to authentication is hidden under the accounts sub-directory
    path('accounts/', include('django.contrib.auth.urls')),

    # temporary pages for displaying cases
    path('poscase/', views.poscase, name="poscase"),

]
