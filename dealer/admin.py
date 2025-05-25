from django.contrib import admin
from dealer.models import User,Category,Dealer_profile,Medicine,Cart,Order

# Register your models here.

admin.site.register(User)

admin.site.register(Category)

admin.site.register(Dealer_profile)

class MedicineAdmin(admin.ModelAdmin):

    exclude=("owner",)

    def save_model(self,request,obj,form,change):

        if not change:

            obj.owner=request.user

            return super().save_model(request,obj,form,change)
    

admin.site.register(Medicine,MedicineAdmin)

admin.site.register(Cart)

admin.site.register(Order)
