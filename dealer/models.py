from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.

class User(AbstractUser):

    ROLE_OPTIONS=(
        ('dealer','dealer'),
        ('customer','customer'),
    )

    role=models.CharField(max_length=15,choices=ROLE_OPTIONS,default='customer')

# dealer profile

class Dealer_profile(models.Model):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name='dealer_profile')

    shop_name=models.CharField(max_length=25,null=False)

    phone=models.CharField(max_length=15,null=False)

    location=models.CharField(max_length=50,null=True)
    
    def __str__(self):
        return f"{self.shop_name} ({self.owner.username})"
    
def create_dealer_profile(sender,instance,created,**kwargs):

    if created and instance.role=="dealer":

        Dealer_profile.objects.create(owner=instance)
        
post_save.connect(create_dealer_profile,User)
 

# category model

class Category(models.Model):

    name = models.CharField(max_length=100,unique=True)

    description = models.TextField(blank=True, null=True)
    
    def __str__(self):

        return self.name
    
# medicine class

class Medicine(models.Model):

    name=models.CharField(max_length=50)

    dealer=models.ForeignKey(Dealer_profile,on_delete=models.CASCADE)

    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)

    price=models.DecimalField(max_digits=10,decimal_places=2)

    image=models.ImageField(upload_to="medimages",null=True,blank=True,default="medimages/defaultimage.jpg")

    description=models.TextField()

    discount=models.DecimalField(max_digits=5,decimal_places=2)

    created_at=models.DateTimeField(auto_now_add=True)

    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.dealer.owner.first_name}"

class Cart(models.Model):

    medicine_object=models.ForeignKey(Medicine,on_delete=models.CASCADE)

    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="basket")

    created_at=models.DateTimeField(auto_now=True)

    quantity=models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicine_object.name} ({self.quantity})"
    
class Order(models.Model):

    medicine_object=models.ManyToManyField(Medicine,related_name="products")

    customer=models.ForeignKey(User,on_delete=models.CASCADE,related_name="purchase")

    is_paid=models.BooleanField(default=False)

    total=models.DecimalField(max_digits=10,decimal_places=2,default=0)

    razorpay_order_id=models.CharField(max_length=100,null=True,blank=True)


