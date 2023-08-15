from django.urls import path
from . import views

urlpatterns = [
    path('confirm/', views.driverlogin,name="signin"),
    path('callback/', views.callback),  #呼叫ChatBot
    path('online_waiting/', views.waitorder , name ='waiting'),  #呼叫ChatBot
    path('updateLocation', views.updateLocation , name = 'updateLocation'),
    # # path('startdriving',views.starting,name='startdriving'),
    path('none_ride_request',views.none_ride_request,name="none_ride_request"),
    path('go_arriving/',views.go_arriving,name='go_arriving'),
    path('go_departing/',views.go_departing,name='go_departing'),
    # #乘客端程式
    path('booking_init/', views.booking_init , name = "booking_init"), 
    path('delete_request/',views.delete_request , name='delete_request'),
    path('cancel_request/' , views.cancel_request , name="cancel_request"),

    path('createRsv' ,views.create_request, name='createRsv' ),
    # path('estimateRequest' ,views.estimate_request , name='estimateRequest' ),
    path('process_request/' ,views.process_request , name='sendREQ' ),
]
