from django import forms
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

# -----------------------------------Account form--------------------------------------------
class RegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super(RegistrationForm,self).save(commit=False)
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user

class editForm(UserChangeForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
    def save(self, commit=True):
        user = super(editForm,self).save(commit=False)
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user

    
# -------------------------------------Book App-----------------------------------------------------
class BookForm(forms.ModelForm):
    startDate=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'date'}))
    endDate=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'date'}))
    class Meta:
        model=Book
        fields=('source','destination','startDate','endDate','securityDeposit','discountId','vehicle',)


# -------------------------------------Driver App-----------------------------------------------------
class DriverForm(forms.ModelForm):
    class Meta:
        model=Driver
        fields=('firstName','lastName','nationalId','address','email','phoneNumber','licenseCategory',)


# -------------------------------------Repair App-----------------------------------------------------
class RepairForm(forms.ModelForm):
    class Meta:
        model=Repair
        fields=('issue','vehicle',)

# -------------------------------------Vehical App-----------------------------------------------------
class VehicleForm(forms.ModelForm):
    class Meta:
        model=Vehicle
        fields = ('cost_per_km','price','registration_plate','no_of_km_travelled','mileage','vehicle_type','fuel_type','insurance_status','image')
