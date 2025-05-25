from django.contrib.auth.forms import UserCreationForm

from dealer.models import User

from django import forms 


class CustomerCreateForm(UserCreationForm):

    class Meta:

        model=User

        fields=["username","password1","password2","email"]

class CustomerSigninForm(forms.Form):

    username=forms.CharField()

    password=forms.CharField()

    



