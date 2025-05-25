from django.contrib.auth.forms import UserCreationForm
from dealer.models import User


class DealerCreateForm(UserCreationForm):

    class Meta:

        model=User

        fields=["username","email","password","password2","first_name"]