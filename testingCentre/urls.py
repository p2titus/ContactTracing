from django.urls import path
from . import views

app_name = 'testingCentre'
urlpatterns = [
    # ex: /testingCentre/
    path('', views.LoginView.as_view(), name='login'),
    # ex: /testingCentre/choose/
    path('choose/', views.ChooseInputMethodView.as_view(), name='chooseInputMethod'),
    # ex: /testingCentre/CSV/
    path('CSV/', views.InputCSVView.as_view(), name='csv'),
    # ex: /testingCentre/singleTest/
    path('singleTest/', views.InputSingleTestView.as_view(), name='singleTest'),
    # /testingCentre/thanks/
    path('singleTest/thanks/', views.thanks, name='thanks'),
    # /testingCentre/singleTest/addPerson
    path('singleTest/addPerson/', views.add_person, name='add person'),

    # path('singleTest/enterResult/', views.thanks, name='thanks'),

]