from django.contrib import admin
from .models import*
from django.utils.html import format_html

class SupplierLocationDetailAdmin(admin.ModelAdmin):
    list_display = ('address_line', 'city', 'state', 'country','pincode')
    search_fields = ('city', 'state', 'country')

@admin.register(SupplierProfile)
class SupplierDetailAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_first_name', 'get_last_name')  
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

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
    list_filter = ('is_approved',)

@admin.action(description="✅ Approve selected tankers")
def approve_selected(modeladmin, request, queryset):
    # Update the related WaterTankerDocument instances
    updated = 0
    for tanker in queryset:
        if tanker.document:
            tanker.document.is_approved = "Approved"
            tanker.document.save()
            updated += 1
    modeladmin.message_user(request, f"{updated} tanker document(s) approved.")

@admin.action(description="❌ Reject selected tankers")
def reject_selected(modeladmin, request, queryset):
    # Update the related WaterTankerDocument instances
    updated = 0
    for tanker in queryset:
        if tanker.document:
            tanker.document.is_approved = "Rejected"
            tanker.document.save()
            updated += 1
    modeladmin.message_user(request, f"{updated} tanker document(s) rejected.")


class TankerDetailAdmin(admin.ModelAdmin):
    list_display = (
        'get_water_tanker_name', 'get_is_approved',
        'view_driving_license', 'view_aadhar_card',
        'view_pan_card', 'view_registration_cert', 'view_vehicle_insurance',
        'view_vehicle_permit',
    )
    readonly_fields = (
        'view_driving_license', 'view_aadhar_card',
        'view_pan_card', 'view_registration_cert', 'view_vehicle_insurance',
        'view_vehicle_permit',
    )
    actions = [approve_selected, reject_selected]

    def get_water_tanker_name(self, obj):
        return obj.document.water_tanker_name if obj.document else "N/A"
    get_water_tanker_name.short_description = "Tanker Name"

    def get_is_approved(self, obj):
        return obj.document.is_approved if obj.document else "N/A"
    get_is_approved.short_description = "Approval Status"

    # Reusable helper for file links
    def render_file_link(self, file_field, label):
        if file_field:
            return format_html('<a href="{}" target="_blank" style="color:green;">✅ {}</a>', file_field.url, label)
        return format_html('<span style="color:red;">❌ Not uploaded</span>')

    def view_driving_license(self, obj):
        return self.render_file_link(obj.document.driving_license, "View License") if obj.document else "N/A"

    def view_aadhar_card(self, obj):
        return self.render_file_link(obj.document.aadhar_card, "View Aadhar") if obj.document else "N/A"

    def view_pan_card(self, obj):
        return self.render_file_link(obj.document.pan_card, "View PAN") if obj.document else "N/A"

    def view_registration_cert(self, obj):
        return self.render_file_link(obj.document.registration_cert, "View RC") if obj.document else "N/A"

    def view_vehicle_insurance(self, obj):
        return self.render_file_link(obj.document.vehicle_insurance, "View Insurance") if obj.document else "N/A"

    def view_vehicle_permit(self, obj):
        return self.render_file_link(obj.document.vehicle_permit, "View Permit") if obj.document else "N/A"

  
admin.site.register(LocationDetail,SupplierLocationDetailAdmin)
admin.site.register(DriverDetail,DriverDetailAdmin)
admin.site.register(DriverAvailability,DriverAvailabilityAdmin)
admin.site.register(WaterTankerDocument,WaterTankerDocumentAdmin)
admin.site.register(TankerDetail,TankerDetailAdmin)