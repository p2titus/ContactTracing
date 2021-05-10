from django.urls import path, include
from . import views

app_name = 'testingCentre'
urlpatterns = [
    # ex: /testingCentre/choose/
    path('choose/', views.ChooseInputMethodView.as_view(), name='chooseInputMethod'),
    # ex: /testingCentre/multipleTests/
    path('multipleTests/', views.InputMultipleTestsView.as_view(), name='multipleTests'),
    # /testingCentre/multipleTests/thanks/
    path('multipleTests/thanks/', views.ResultEnteredView.as_view(), name='multipleTestsThanks'),
    # /testingCentre/multipleTests/error/
    path('multipleTests/error/', views.DataFormatErrorView.as_view(), name='multipleTestsError'),
    # ex: /testingCentre/singleTest/
    path('singleTest/', views.InputSingleTestView.as_view(), name='singleTest'),
    # /testingCentre/thanks/
    path('singleTest/thanks/', views.ResultEnteredView.as_view(), name='thanks'),
    # /testingCentre/singleTest/addPerson
    path('singleTest/addPerson/', views.add_person, name='add person'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/logged_in/', views.loggedIn, name='logged_in'),
    path('accounts/logout/logout', views.logout, name='logout'),

    # path('singleTest/enterResult/', views.thanks, name='thanks'),

]
