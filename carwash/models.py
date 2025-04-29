from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Photo(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(upload_to='gallery/', verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Слайдер"
        verbose_name_plural = "Слайды"

class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='logo/', verbose_name="Логотип")
    company_name = models.CharField(max_length=100, verbose_name="Название компании")

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

class WashingSpot(models.Model):
    SPOT_NUMBERS = [(i, f"Место {i}") for i in range(1, 11)]
    SERVICE_CHOICES = [
        ('express', 'Экспресс-мойка (500 ₽)'),
        ('full', 'Полный комплекс (1500 ₽)'),
        ('detailing', 'Детейлинг (2500 ₽)'),
    ]

    number = models.IntegerField(choices=SPOT_NUMBERS, verbose_name="Номер места")
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, verbose_name="Услуга")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        unique_together = ['number', 'service']
        verbose_name = "Место для мойки"
        verbose_name_plural = "Места для мойки"

    def __str__(self):
        return f"Место {self.number} ({self.get_service_display()})"

class Booking(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    spot = models.ForeignKey(WashingSpot, on_delete=models.CASCADE, verbose_name="Место", null=True)
    date = models.DateTimeField(verbose_name="Дата и время")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.user.username if self.user else 'Аноним'} - {self.spot}"

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10)  # Сохраняем emoji

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Услуги"
        verbose_name_plural = "Услуги"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, verbose_name="Бронирование")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты")

    def __str__(self):
        return f"Заказ {self.id} - {self.user.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    reply = models.TextField(blank=True, null=True, verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата ответа")
    is_replied = models.BooleanField(default=False, verbose_name="Отвечено")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"

    
    






    