from django import forms
from .models import Student



class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'phone', 'direction', 'monthly_amount']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': "O'quvchi F.I.Sh"
            }),
            'phone': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': "+998 90 123 45 67"
            }),
            'direction': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': "Masalan: Frontend"
            }),
            # type="number" + step="1000" — foydalanuvchi to'g'ridan-to'g'ri
            # haqiqiy summani kiritadi (masalan 1000000), hech qanday
            # ko'paytirish backendda BO'LMAYDI.
            'monthly_amount': forms.NumberInput(attrs={
                'class': 'glass-input',
                'placeholder': '1000000',
                'step': '1000',
                'min': '0',
            }),
        }

    def clean_monthly_amount(self):
        # Aynan shu yerda "min so'm" yoki formatlangan qiymatlar
        # (masalan "1.000.000" yoki "1,000,000") noto'g'ri parse bo'lib,
        # keyin backendda ko'paytirilib ketishining oldini olamiz.
        amount = self.cleaned_data.get('monthly_amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("Summa manfiy bo'lishi mumkin emas.")
        return amount

    def clean_payment_day(self):
        day = self.cleaned_data.get('payment_day')
        if day is not None and not (1 <= day <= 31):
            raise forms.ValidationError("To'lov kuni 1 dan 31 gacha bo'lishi kerak.")
        return day