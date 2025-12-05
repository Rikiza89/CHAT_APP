# apps/accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match')
        return cd['password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    status_message = forms.CharField(max_length=200, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'avatar', 'status_message']