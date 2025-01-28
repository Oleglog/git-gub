from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages

def home_page(request):
    return render(request, 'carwash/index.html')

def services_page(request):
    return render(request, 'carwash/services.html')

def prices_page(request):
    return render(request, 'carwash/prices.html')

def gallery_page(request):
    return render(request, 'carwash/gallery.html')

def contacts_page(request):
    return render(request, 'carwash/contacts.html')

def contacts_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Отправка email (пример)
        send_mail(
            f"Сообщение от {name}",
            message,
            email,
            ['info@cleanauto.ru'],
            fail_silently=False,
        )
        
        messages.success(request, 'Ваше сообщение отправлено!')
        return redirect('contacts')
    
    return render(request, 'carwash/contacts.html')