from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.urls import reverse
from users.models import CustomerUser
from django.db.models import Avg, Count
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox





class Ip(models.Model): #  таблица где будут айпи адреса
    ip = models.CharField(max_length=350)

    def __str__(self):
        return self.ip


class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    image = models.ImageField(blank=True, upload_to='category_images/%Y/%m/%d/')
    status = models.CharField(max_length=10, choices=STATUS)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('category', kwargs={"category_id": self.pk})

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



class Brand(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True,  verbose_name='Наименование категории')
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="brand_images/%Y/%m/%d/", blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])



    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'


class Slider(models.Model):
    categories = models.ForeignKey(Category, on_delete=models.PROTECT, null=True,  blank=True ,verbose_name='Наименование категории')
    brands = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True,  blank=True ,verbose_name='Наименование бренда')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="brand_images/%Y/%m/%d/")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Slider'
        verbose_name_plural = 'Sliders'



class Color(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True,null=True)


    def __str__(self):
        return self.title

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'



class Size(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'



#     minamount = models.IntegerField(default=3, blank=True, null=True, verbose_name='минимальная сумма') # minamount УДАЛИТЬ НАДО


class Product(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),

    )


    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True,  verbose_name='Наименование категории')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True,  verbose_name='Наименование бренда')
    title = models.CharField(max_length=10000, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='Цена')
    old_price = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='старая цена')
    product_code = models.IntegerField(default=1, verbose_name='Код товара')
    description = models.TextField(verbose_name=' описания товара')
    detail = models.TextField(verbose_name='Характеристики или подробное описания товара ')
    amount = models.IntegerField(default=0, verbose_name='Количество товара')
    image = models.ImageField(upload_to='image/%Y/%m/%d/')
    status = models.CharField(max_length=10, choices=STATUS, verbose_name='в наличии True')
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    favourites = models.ManyToManyField(CustomerUser, related_name='favourite', default=None, blank=True)
    comparison = models.ManyToManyField(CustomerUser, related_name='compare', default=None, blank=True)
    views = models.ManyToManyField(Ip, related_name="post_views", blank=True) # подсчет количества ip адресов
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""

    def get_absolute_url(self):
        return reverse('product', kwargs={"pk": self.pk})

    def save(self, *args, **kwargs): # автоматически увеличивает код товара (product_code)
        if self._state.adding:
            last_id = Product.objects.all().aggregate(largest=models.Max('product_code'))['largest']
            if last_id is not None:
                self.product_code= last_id + 1
        super(Product, self).save(*args, **kwargs)




    def total_views(self): # получить количество просмотров
        return self.views.count()



    def avaregereview(self):  # Подсчет количества рейтинга
        reviews = Comment.objects.filter(product=self).aggregate(avarage=Avg('rate'))
        avg=0
        if reviews["avarage"] is not None:
            avg=float(reviews["avarage"])
        return avg

    def countreview(self): # Подсчет количества комментарии
        reviews = Comment.objects.filter(product=self).aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt



    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']


class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to='images/%Y/%m/%d/')

    def __str__(self):
        return self.title


class Variants(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)
    image_id = models.IntegerField(blank=True, null=True, default=0)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='Цена')

    def __str__(self):
        return str(self.title)


    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            varimage = img.image.url
        else:
            varimage = ""
        return varimage

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""

    class Meta:
        verbose_name = 'Вариант'
        verbose_name_plural = 'Варианты'


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    username = models.CharField(max_length=150, verbose_name='Name')
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    likes = models.ManyToManyField(CustomerUser, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(CustomerUser, blank=True, related_name='dislikes')
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class CommentForm(ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox) # product-detail строка: 522 class="g-recaptcha"
    class Meta:
        model = Comment
        fields = ['username', 'comment', 'rate', 'captcha']




class Stock(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    data = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='True')
    is_published = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title

#     sale = models.IntegerField('Скидка в процентах', blank=True, default=0)


    def get_sale(self):
        '''Расчитать стоимость со скидкой'''
        price = int(self.product.price * (100 - self.product.old_price) / 100)
        return price

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'


class CategoryLangEn(MPTTModel):
    category = models.ForeignKey(Category, related_name='categorylangs', on_delete=models.CASCADE)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(null=False, unique=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Язык категори EN'
        verbose_name_plural = 'Языки категории EN'



class ProductLangEN(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #many to one relation with Category
    category = models.ForeignKey(CategoryLangEn, on_delete=models.PROTECT,  null=True, blank=True)
    title = models.CharField(max_length=10000, verbose_name='Наименование')
    description = models.TextField(verbose_name=' описания товара')
    detail = models.TextField(verbose_name='Характеристики или подробное описания товара ')
    slug = models.SlugField(null=False, unique=True)



    def __str__(self):
        return self.title


    class Meta:
        verbose_name = 'Язык продукта EN'
        verbose_name_plural = 'Языки продукта EN'


