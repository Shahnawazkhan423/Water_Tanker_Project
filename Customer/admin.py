from django.contrib import admin
from .models import LocationDetail, UserDetail, Feedback, OrderDetail, Payment

class LocationDetailAdmin(admin.ModelAdmin):
    list_display = ('address_line', 'city', 'state', 'country')
    search_fields = ('city', 'state', 'country')


class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'email', 'location')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('location__city', 'location__state')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating_value', 'feedback_date')
    list_filter = ('rating_value', 'feedback_date')
    search_fields = ('user__first_name', 'user__last_name')


class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'driver', 'tanker', 'order_status', 'order_date', 'delivery_date')
    list_filter = ('order_status', 'order_date')
    search_fields = ('user__first_name', 'driver__user__first_name')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'payment_status', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('transaction_id',)


admin.site.register(UserDetail,UserDetailAdmin)
admin.site.register(LocationDetail,LocationDetailAdmin)
admin.site.register(Feedback,FeedbackAdmin)
admin.site.register(OrderDetail,OrderDetailAdmin)
admin.site.register(Payment,PaymentAdmin)
