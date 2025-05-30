from django.contrib import admin
from .models import*
# Register your models here.
class SupplierLocationDetailAdmin(admin.ModelAdmin):
    list_display = ('address_line', 'city', 'state', 'country')
    search_fields = ('city', 'state', 'country')

class DriverAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('availability_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'availability_date')
    search_fields = ('notes',)

class DriverDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability')
    list_filter = ('availability__status','availability')
    search_fields = ('user__first_name', 'user__last_name')

class WaterTankerDocumentAdmin(admin.ModelAdmin):
    list_display = ('water_tanker_name', 'upload_date')
    search_fields = ('water_tanker_name',)

class TankerDetailAdmin(admin.ModelAdmin):
    list_display = ('capacity', 'category', 'driver', 'available')
    list_filter = ('available', 'category')

admin.site.register(SupplierProfile)
admin.site.register(LocationDetail,SupplierLocationDetailAdmin)
admin.site.register(DriverDetail,DriverDetailAdmin)
admin.site.register(DriverAvailability,DriverAvailabilityAdmin)
admin.site.register(WaterTankerDocument,WaterTankerDocumentAdmin)
admin.site.register(TankerDetail,TankerDetailAdmin)