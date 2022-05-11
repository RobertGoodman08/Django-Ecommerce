from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import TextInput, EmailInput, Select, FileInput
from users.models import CustomerUser, UserProfile
from django.utils.translation import gettext_lazy as _


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-fname', 'placeholder': _('Имя пользователя')}))
    email = forms.EmailField(max_length=200, widget=forms.EmailInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-email', 'placeholder': _('Email')}))
    first_name = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-fname', 'placeholder': _('Имя')}))
    last_name = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-lname', 'placeholder': _('Фамилия')}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-password', 'placeholder': _('Пароль')}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text input-text--primary-style', 'id': 'reg-password', 'placeholder': _('Подтвердите пароль')}))

    class Meta:
        model = CustomerUser
        fields = ('username', 'email','first_name','last_name', 'password1', 'password2', )




class UserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomerUser
        fields = ('username','email','first_name','last_name')
        widgets = {
            'username': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'username'}),
            'email': EmailInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'email'}),
            'first_name': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'first_name'}),
            'last_name': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'last_name' }),
        }

COUNTRY = [
    ('Азербайджанскую', 'Азербайджанскую'),
    ('Армения', 'Армения'),
    ('Беларусь', 'Беларусь'),
    ('Казахстан', 'Казахстан'),
    ('Кыргызскую', 'Кыргызскую'),
    ('Молдова', 'Молдова'),
    ('Россия', 'Россия'),
    ('Таджикистан', 'Таджикистан'),
    ('Туркмения', 'Туркмения'),
    ('Узбекистан', 'Узбекистан'),
    ('Украину', 'Украину'),
]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'country','city','image')
        widgets = {
            'phone': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'phone'}),
            'address': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'address'}),
            'country': Select(attrs={'class': 'gl-label','placeholder':'city'},choices=COUNTRY),
            'city': TextInput(attrs={'class': 'input-text input-text--primary-style','placeholder':'country' }),
            'image': FileInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'image', }),
        }