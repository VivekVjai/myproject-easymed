from django.shortcuts import render,redirect
from django.views.generic import View
from dealer.forms import DealerCreateForm


# Create your views here.
class DealerCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=DealerCreateForm()

        return render (request,"dealer_register.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=DealerCreateForm(form_data)

        if form_instance.is_valid():

            form_instance.instance.role="dealer"

            form_instance.instance.is_superuser=True

            form_instance.instance.is_staff=True

            form_instance.save()

            return redirect("/admin/login/")
        
        else:

            return redirect(request,"dealer_register.html",{"form":form_instance})


