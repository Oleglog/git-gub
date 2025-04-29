from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Exists, OuterRef
from datetime import datetime
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Photo, SiteSettings, Service, WashingSpot, Booking, Order, ContactMessage
from .forms import BookingForm
from .forms_auth import RegisterForm, ProfileForm
from .models import Profile
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def gallery(request):
    photos = Photo.objects.all()
    return render(request, 'carwash/gallery.html', {'photos': photos})

def home_page(request):
    # Эта функция должна быть доступна всем пользователям
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Если пользователь не авторизован, перенаправляем на страницу входа
            messages.error(request, 'Для бронирования необходимо войти в систему')
            return redirect('login')
            
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Проверяем, не занято ли место
            existing_booking = Booking.objects.filter(
                spot=booking.spot,
                date=booking.date
            ).exists()
            
            if existing_booking:
                messages.error(request, 'Это место уже занято на выбранное время!')
                return redirect('home')
            
            booking.save()
            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm()

    context = {
        'form': form,
        'site_settings': SiteSettings.objects.first()
    }
    return render(request, 'carwash/index.html', context)

def services_page(request):
    services = Service.objects.all()
    return render(request, 'carwash/services.html', {'services': services})

def about(request):
    return render(request, 'carwash/about.html')

def contacts_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Сохраняем сообщение в базе данных
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        # Отправляем уведомление администратору
        try:
            send_mail(
                subject=f'Новое сообщение от {name}',
                message=f"""
                Новое сообщение с сайта:
                
                Имя: {name}
                Email: {email}
                Сообщение:
                {message}
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
        except:
            messages.error(request, 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.')
        
        return redirect('contacts')
        
    return render(request, 'carwash/contacts.html')

def base_context(request):
    site_settings = SiteSettings.objects.first()
    return {'site_settings': site_settings}


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                phone=form.cleaned_data['phone']
            )
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'carwash/register.html', {'form': form})

@login_required
def profile_view(request):
    # Если пользователь админ, перенаправляем в админку
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin:index')
    
    # Для обычных пользователей показываем профиль
    profile = request.user.profile
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'carwash/profile.html', {
        'form': form,
        'bookings': bookings,
        'orders': orders
    })

def login_view(request):
    # Если пользователь уже авторизован, перенаправляем на главную
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Получаем URL для перенаправления или используем 'home' по умолчанию
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверные логин или пароль')
    return render(request, 'carwash/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')  # Прямой редирект на главную

def get_spots(request):
    service = request.GET.get('service')
    date_str = request.GET.get('date')
    
    if not all([service, date_str]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    try:
        # Получаем все места для выбранной услуги
        spots = WashingSpot.objects.filter(service=service)
        
        # Получаем все бронирования на выбранную дату для этой услуги
        booked_spots = Booking.objects.filter(
            spot__service=service,
            date__year=date.year,
            date__month=date.month,
            date__day=date.day,
            date__hour=date.hour
        ).values_list('spot_id', flat=True)

        spots_data = []
        for spot in spots:
            # Проверяем, есть ли бронирование для этого места
            is_booked = spot.id in booked_spots
            
            spots_data.append({
                'id': spot.id,
                'number': spot.number,
                'is_available': spot.is_active and not is_booked,
                'booked_by': None  # Можно добавить информацию о том, кто забронировал
            })

        return JsonResponse({'spots': spots_data})
    
    except Exception as e:
        print(f"Error processing spots: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def get_service_price(service):
    prices = {
        'express': 500,
        'full': 1500,
        'detailing': 2500
    }
    return prices.get(service, 0)

@login_required
def payment_page(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        # Проверяем, существует ли уже оплаченный заказ для этого бронирования
        order = Order.objects.get(booking=booking)
        if order.status == 'paid':
            messages.warning(request, 'Этот заказ уже оплачен')
            return redirect('home')
    except Order.DoesNotExist:
        # Если заказа нет, создаем новый
        order = Order.objects.create(
            booking=booking,
            user=request.user,
            amount=get_service_price(booking.spot.service),
            status='pending'
        )
    except:
        messages.error(request, 'Бронирование не найдено')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'pay':
            # Обработка оплаты
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            response = redirect('order_confirmation', order_id=order.id)
            # Добавляем заголовки для предотвращения кэширования
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
            
        elif action == 'cancel':
            # Отмена заказа
            order.status = 'cancelled'
            order.save()
            booking.delete()
            messages.info(request, 'Заказ отменен')
            return redirect('home')

    response = render(request, 'carwash/payment.html', {
        'booking': booking,
        'order': order
    })
    # Добавляем заголовки для предотвращения кэширования
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    booking = order.booking
    
    # Формируем текст письма
    message = f"""
    Здравствуйте, {request.user.username}!
    
    Ваш заказ №{order.id} успешно оформлен и оплачен.
    
    Детали заказа:
    - Дата и время: {booking.date.strftime('%d.m.Y %H:%M')}
    - Услуга: {booking.spot.get_service_display()}
    - Место: {booking.spot.number}
    - Сумма: {order.amount} ₽
    
    Пожалуйста, приезжайте за 5-10 минут до назначенного времени.
    
    С уважением,
    Команда "Чистое авто"
    """
    
    # Пытаемся отправить email
    try:
        send_mail(
            subject=f'Подтверждение заказа №{order.id} - Чистое авто',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        messages.success(request, 'Информация о заказе отправлена на вашу почту')
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        messages.error(request, 'Не удалось отправить информацию на почту')
    
    return render(request, 'carwash/order_confirmation.html', {
        'order': order,
        'booking': booking
    })


