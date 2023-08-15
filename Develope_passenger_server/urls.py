from django.urls import path
from . import views

urlpatterns = [
    path('booking/',views.booking , name='bookRide'),
    path("callback/",views.callback)
]
