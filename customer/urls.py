from django.urls import path
from customer import views

urlpatterns=[
    path("create/",views.CustomerCreateView.as_view(),name="cus-create"),
    path("signin/",views.CustomerSigninView.as_view(),name="cus-signin"),
    path("index/",views.IndexView.as_view(),name="home"),
    path("dealerlist/",views.DealerlistView.as_view(),name="dealer-list"),
    path("dealermedlist/<int:pk>/med/",views.DealerMedicineView.as_view(),name="dealer-medlist"),
    path("dealermed/<int:pk>/add-to-cart/",views.AddtoCartView.as_view(),name="cartadd"),
    path("medicine/<int:pk>/compare-price/",views.ComparePrice.as_view(),name="pricecompare"),
    path("categories/<int:pk>/medicines/",views.Medicines_by_categories.as_view(),name="medicines_by_category"),
    path("cartsummary/",views.CartSummaryView.as_view(),name="cart_summary"),
    path("cart/<int:pk>/remove/",views.CartItemDelete.as_view(),name="cart_remove"),
    path("checkout/",views.CheckOutview.as_view(),name="checkout"),
    path("payment/",views.Paymentview.as_view(),name="payment"),
    path("myorders/",views.MyOrderView.as_view(),name="orders"),
    path("signout/",views.SignOutView.as_view(),name="sign-out"),
]