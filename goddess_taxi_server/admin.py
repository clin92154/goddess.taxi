from django.contrib import admin
from .models import *
from django.forms import Textarea
from django.contrib.postgres.fields import JSONField
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'car_no', 'is_online']
    search_fields = ['name', 'driver_group__driver_group', 'car_no']
    formfield_overrides = {
        JSONField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }
class DriverGroupAdmin(admin.ModelAdmin):
    list_display = ['driver_group', 'drivers_list']
    search_fields = ['driver_group']
    
    def drivers_list(self, obj):
        drivers = obj.driver_set.all()
        return ', '.join([driver.driver_name for driver in drivers])

admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverGroup)
admin.site.register(RideRequest)
admin.site.register(Passengers)
admin.site.register(RideRSV)




