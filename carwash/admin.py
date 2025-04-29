from django.contrib import admin
from .models import Photo, SiteSettings, Booking, Service, WashingSpot, Order, ContactMessage
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('company_name',)

class OrderInline(admin.StackedInline):
    model = Order
    extra = 0
    readonly_fields = ('created_at', 'paid_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'spot', 'date', 'get_amount', 'get_status', 'created_at')
    list_filter = ('spot', 'created_at', 'order__status')
    search_fields = ('name', 'phone', 'user__username')
    inlines = [OrderInline]
    
    def get_amount(self, obj):
        return obj.order.amount if hasattr(obj, 'order') else '-'
    get_amount.short_description = 'Сумма'
    
    def get_status(self, obj):
        return obj.order.status if hasattr(obj, 'order') else '-'
    get_status.short_description = 'Статус'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    search_fields = ('name', 'description')

@admin.register(WashingSpot)
class WashingSpotAdmin(admin.ModelAdmin):
    list_display = ('number', 'get_service_display', 'is_active')
    list_filter = ('service', 'is_active')
    search_fields = ('number',)
    list_editable = ('is_active',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_replied', 'replied_at')
    list_filter = ('is_replied', 'created_at', 'replied_at')
    search_fields = ('name', 'email', 'message', 'reply')
    readonly_fields = ('created_at',)
    fields = ('name', 'email', 'message', 'reply', 'is_replied', 'replied_at')

    def save_model(self, request, obj, form, change):
        if 'reply' in form.changed_data and obj.reply:
            # Если добавлен ответ, отправляем его на email пользователя
            try:
                send_mail(
                    subject='Ответ на ваше сообщение - Чистый Авто',
                    message=obj.reply,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
                obj.is_replied = True
                obj.replied_at = timezone.now()
            except Exception as e:
                messages.error(request, f'Ошибка при отправке ответа: {str(e)}')
        super().save_model(request, obj, form, change)






