import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтвердите пароль',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = re.sub(r'\D', '', phone)
        if digits and len(digits) < 7:
            raise forms.ValidationError('Введите корректный номер телефона.')
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('password_confirm')
        if password and confirm and password != confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        raw = self.cleaned_data['password']
        # username = email prefix, guaranteed unique by clean_email
        user.username = self.cleaned_data['email'].split('@')[0]
        # ensure username uniqueness
        base = user.username
        counter = 1
        while User.objects.filter(username=user.username).exists():
            user.username = f'{base}{counter}'
            counter += 1
        user.email = self.cleaned_data['email']
        user.set_password(raw)
        if commit:
            user.save()
        return user
    



class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput,
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )
 
    def clean_email(self):
        return self.cleaned_data.get('email', '').lower()
 

class TwoFactorForm(forms.Form):
    code = forms.CharField(
        label='Код подтверждения',
        max_length=6,
        min_length=6,
        widget=forms.TextInput,
    )
 
    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit():
            raise forms.ValidationError('Код должен состоять из 6 цифр.')
        return code