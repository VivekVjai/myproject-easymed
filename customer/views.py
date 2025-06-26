from django.shortcuts import render,redirect

from django.views.generic import View,CreateView,FormView

from customer.forms import CustomerCreateForm,CustomerSigninForm

from django.urls import reverse_lazy

from django.contrib.auth import authenticate,login,logout

from dealer.models import Dealer_profile,Medicine,Cart,Order,Category

from django.shortcuts import get_object_or_404

from django.db.models import Sum

from django.conf import settings

import razorpay

from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages

from customer.decorators import signin_required

# Create your views here.

class CustomerCreateView(CreateView):

    template_name="customer_create.html"

    form_class=CustomerCreateForm

    success_url=reverse_lazy("cus-signin")

class CustomerSigninView(FormView):

    template_name="customer_signin.html"

    form_class=CustomerSigninForm

    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=CustomerSigninForm(form_data)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            uname=data.get("username")

            pwd=data.get("password")

            user_instance=authenticate(request, username=uname, password=pwd)

            print("Authenticated user:", user_instance)

            if user_instance:
                
                login(request, user_instance)

                if user_instance.role=="customer":

                    return redirect("home")
                    
                else:
                    
                    return render(request,"customer_signin.html",{"form":form_instance})


@method_decorator(signin_required,name="dispatch")
class IndexView(View):

    def get(self,request,*args,**kwargs):

        all_dealers=Dealer_profile.objects.all()

        all_medicines=Medicine.objects.all()

        all_categories=Category.objects.all()

        return render(request,"index.html",{"dealers":all_dealers,"medicines":all_medicines,"categories":all_categories})


@method_decorator(signin_required,name="dispatch")
class DealerlistView(View):

    def get(self,request,*args,**kwargs):
        
        dealers=Dealer_profile.objects.all()

        return render(request,"dealers.html",{"dealer_list":dealers})


@method_decorator(signin_required,name="dispatch")
class Medicines_by_categories(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        category=get_object_or_404(Category,id=id)

        medicines=Medicine.objects.filter(category=category)

        return render(request,"medicine_by_category.html",{"category":category,"medicines":medicines})


@method_decorator(signin_required,name="dispatch")
class DealerMedicineView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        dealer=get_object_or_404(Dealer_profile,id=id)

        medicines=Medicine.objects.filter(dealer=dealer)

        return render(request,"medicinelist.html",{"medicine_list":medicines,"dealer":dealer})


@method_decorator(signin_required,name="dispatch")
class AddtoCartView(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        medicine_instance=get_object_or_404(Medicine,id=id)
        quantity=int(request.POST.get("quantity",1))

        cart_instance,created=Cart.objects.get_or_create(
            medicine_object=medicine_instance,
            user=request.user,
            defaults={"quantity":quantity})
        
        if not created:
            cart_instance.quantity += quantity
            cart_instance.save()

        return redirect("dealer-list") 


@method_decorator(signin_required,name="dispatch")
class ComparePrice(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        medicine=get_object_or_404(Medicine,id=id)

        same_meds=Medicine.objects.filter(name__iexact=medicine.name).exclude(id=medicine.id)

        context={"medicine":medicine,"same_meds":same_meds}

        return render(request,"compare_price.html",context)


@method_decorator(signin_required,name="dispatch")
@method_decorator(signin_required, name="dispatch")
class CartSummaryView(View):

    def get(self, request, *args, **kwargs):

        cart_items = Cart.objects.filter(user=request.user).select_related("medicine_object")

        total = 0

        for item in cart_items:
            price = item.medicine_object.price
            discount = item.medicine_object.discount
            quantity = item.quantity  

            discounted_price = price - (price * discount / 100)
            total_price = discounted_price * quantity  

            item.discounted_price = round(discounted_price, 2)
            item.total_price = round(total_price, 2) 

            total += total_price

        context = {
            "cart": cart_items,
            "total": round(total, 2)
        }

        return render(request, "cart_summary.html", context)


@method_decorator(signin_required,name="dispatch")
class CartItemDelete(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        cart_instance=Cart.objects.get(id=id)

        if cart_instance.user != request.user:

            return redirect("home")
        
        cart_instance.delete()

        return redirect("cart_summary")


@method_decorator(signin_required,name="dispatch")
class CheckOutview(View):

    def get(self,request,*args,**kwargs):

        cart_items=request.user.basket.all()

        order_total=0

        for item in cart_items:

            price=item.medicine_object.price

            discount=item.medicine_object.discount

            discounted_price=price - (price*discount/100)

            item_total = discounted_price * item.quantity

            item.discounted_price = round(discounted_price, 2)

            item.total_price = round(item_total, 2)

            order_total+=item_total

        if order_total ==0:
            return redirect("cart_summary")

        order_instance=Order.objects.create(customer=request.user,total=order_total)

        for ci in cart_items:

            order_instance.medicine_object.add(ci.medicine_object)


        client= razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

        razorpay_order=client.order.create({
            "amount":int(order_total*100),
            "currency":"INR",
            "receipt":f"order_rcptid_{order_instance.id}",
            "payment_capture":1
        })

        order_instance.razorpay_order_id= razorpay_order['id']

        order_instance.save()

        context={
            "order":order_instance,
            "cart_items": cart_items,
            "razorpay_key":settings.RAZORPAY_KEY_ID,
            "amount":order_total,
            "razorpay_order_id":razorpay_order['id'],
            "full_name": request.user.get_full_name(), 
        }

        return render(request,"checkout.html",context)
    
    
class Paymentview(View):

    def post(self,request,*args,**kwargs):

        print(request.POST,"+++++")

        client= razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

        try:

            client.utility.verify_payment_signature(request.POST)

            print("payment success")

            rzp_order_id=request.POST.get("razorpay_order_id")

            order_instance=Order.objects.get(razorpay_order_id=rzp_order_id)

            order_instance.is_paid=True

            order_instance.save()
            
            request.user.basket.all().delete()

            messages.success(request, "Payment successful! Your order has been placed.")

            return redirect("home")

        except razorpay.errors.SignatureVerificationError as e:
                print(" Signature verification failed:", str(e))
        except Order.DoesNotExist:
                print(" Order not found for:", rzp_order_id)
        except Exception as e:
                print(" Unknown error:", str(e))


        return redirect("cart_summary")
    
@method_decorator(signin_required,name="dispatch")    
class MyOrderView(View):

    def get(self,request,*args,**kwargs):

        orders=Order.objects.filter(customer=request.user,is_paid=True).order_by('-id')

        for order in orders:

            meds=list(order.medicine_object.all())

            for med in meds:

                med.final_price = round(med.price - (med.price * med.discount / 100), 2)
            
            order.medicine_object_cached =meds


        return render(request,"my_orders.html",{"orders":orders})

@method_decorator(signin_required,name="dispatch")
class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("cus-signin")

@method_decorator(signin_required,name="dispatch")
class MyAccountDelete(View):

    def post(self,request,*args,**kwargs):

        user=request.user

        user.delete()

        return redirect("cus-create")






        




       






    
    





