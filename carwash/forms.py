from django import forms
from .models import Booking, WashingSpot
from datetime import datetime, time

class BookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-lg'
        }),
        label="Дата"
    )
    
    time = forms.ChoiceField(
        choices=[
            (f"{hour:02d}:00", f"{hour:02d}:00")
            for hour in range(9, 23)  # от 9:00 до 22:00
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg time-select'
        }),
        label="Время"
    )

    service = forms.ChoiceField(
        choices=WashingSpot.SERVICE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        label="Услуга"
    )
    
    spot = forms.ModelChoiceField(
        queryset=WashingSpot.objects.none(),
        widget=forms.HiddenInput(),
        required=True
    )

    class Meta:
        model = Booking
        fields = ['name', 'phone', 'service', 'date', 'time', 'spot']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Иван Иванов'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+7 (999) 123-45-67'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['spot'].queryset = WashingSpot.objects.none()
        
        if 'service' in self.data:
            try:
                service = self.data.get('service')
                self.fields['spot'].queryset = WashingSpot.objects.filter(
                    service=service,
                    is_active=True
                )
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_str = cleaned_data.get('time')
        
        if date and time_str:
            # Преобразуем строку времени в объект time
            hour = int(time_str.split(':')[0])
            time_obj = time(hour=hour)
            
            # Комбинируем дату и время
            cleaned_data['date'] = datetime.combine(date, time_obj)
        
        return cleaned_data