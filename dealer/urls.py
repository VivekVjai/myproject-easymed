from django.urls import path
from dealer import views

urlpatterns=[
    path("register/",views.DealerCreateView.as_view(),name="dealer-register")
]