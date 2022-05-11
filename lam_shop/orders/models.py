from users.models import CustomerUser
from django.db import models
from django.forms import ModelForm
from product.models import Product, Variants



class ShopCart(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(Variants, on_delete=models.SET_NULL, blank=True, null=True)  # relation with varinat
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.title

    @property
    def price(self):
        return (self.product.price)

    @property
    def amount(self):
        return (self.quantity * self.product.price)

    @property
    def varamount(self):
        return (self.quantity * self.variant.price)


    class Meta:
        verbose_name = 'Корзина покупок'


class ShopCartForm(ModelForm):
    class Meta:
        model = ShopCart
        fields = ['quantity']

class Order(models.Model):
    STATUS = (
        ('Новый', 'Новый'),
        ('Принятый', 'Принятый'),
        ('Подготовка', 'Подготовка'),
        ('при доставке', 'при доставке'),
        ('Завершенный', 'Завершенный'),
        ('Отменено', 'Отменено'),
    )
    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=5, editable=False )
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    total = models.FloatField()
    status=models.CharField(max_length=100,choices=STATUS,default='Новый')
    ip = models.CharField(blank=True, max_length=20)
    adminnote = models.CharField(blank=True, max_length=100)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name



    class Meta:
        verbose_name = 'информация о клиенте'
        verbose_name_plural = 'информация о клиенте'

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address', 'phone', 'city', 'country']

class OrderProduct(models.Model):
    STATUS = (
        ('Новый', 'Новый'),
        ('Принятый', 'Принятый'),
        ('Отменено', 'Отменено'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variants, on_delete=models.SET_NULL, blank=True, null=True)  # relation with varinat
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    status = models.CharField(max_length=100, choices=STATUS, default='Новый')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


    class Meta:
        verbose_name = 'заказ принят'
        verbose_name_plural = 'заказы приняты'