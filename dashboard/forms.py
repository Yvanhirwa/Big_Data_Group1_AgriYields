# dashboard/forms.py
from django import forms
from .models import DataSet
from django.contrib.auth.models import User

class UploadFilesForm(forms.Form):
    num_regions = forms.IntegerField(min_value=1, max_value=10, initial=5, label="Number of Regions")
    w1 = forms.FloatField(min_value=0, max_value=1, initial=0.4, label="Weight 1 (Temperature)")
    w2 = forms.FloatField(min_value=0, max_value=1, initial=0.5, label="Weight 2 (Rainfall)")
    w3 = forms.FloatField(min_value=0, max_value=1, initial=0.1, label="Weight 3 (Soil Moisture)")
    
    temp_csv = forms.FileField(label="Temperature CSV")
    rain_csv = forms.FileField(label="Rainfall CSV")
    moisture_csv = forms.FileField(label="Soil Moisture CSV")
    crop_csv = forms.FileField(label="Crop Type CSV")


class PredictForm(forms.Form):
    temperature = forms.FloatField(label="Temperature (°C)", min_value=-50, max_value=60)
    rainfall = forms.FloatField(label="Rainfall (mm/day)", min_value=0, max_value=500)
    soil = forms.FloatField(label="Soil Moisture (%)", min_value=0, max_value=100)


class SignUpForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full', 'placeholder': 'Enter a username', 'autocomplete': 'off'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full', 'placeholder': 'Enter a password', 'autocomplete': 'new-password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full', 'placeholder': 'Confirm your password', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
