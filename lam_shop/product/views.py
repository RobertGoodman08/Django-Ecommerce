from django.shortcuts import render, get_object_or_404, reverse, redirect
from product.models import Category, Product, Variants, Brand, Comment, CommentForm, Ip, \
    Slider, Images, Stock, ProductLangEN, CategoryLangEn
from orders.models import ShopCart
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from users.models import CustomerUser
from django.core.paginator import Paginator, EmptyPage
from lam_shop import settings
from django.views.decorators.cache import cache_page
from django.utils import translation
from currencies.models import Currency
from product.forms import ContactForm
from django.core.mail import send_mail


# {% load cache %}
# {% cache 500 sidebar %}
#     .. sidebar ..
# {% endcache %}
#


# Метод для получения айпи
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR') # В REMOTE_ADDR значение айпи пользователя
    return ip


# @cache_page(60 * 1)
def index(request): # главная страница
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    product = Product.objects.all()
    product_hit = Product.objects.all().order_by('-views') # Хиты продаж
    product_popular = Product.objects.all().order_by('-favourites') # Популярное
    top_discounts = Stock.objects.order_by('?') # Топ-скидки
    product_new = Product.objects.all().order_by('-update_at') # Новинки
    product_random = Product.objects.all().order_by('?') # Купить товары серии random
    brand_top = Brand.objects.all() # Популярные бренды




    product_en = ProductLangEN.objects.all() # Язык продукта на английском
    banner = Brand.objects.order_by('?')
    categories = Category.objects.all() # Menu
    sliders = Slider.objects.all()
    stock = Stock.objects.order_by('?')[::1]

    # InvPortal.objects.values('portal_level').distinct().count()
    # fav = bool # Добавить в список желаний || Удалите из списка желаний
    # if Product.objects.filter(favourites=request.user.id).exists():# добавление в избранное
    #          fav = True

    fav = bool  # Добавить в список желаний || Удалите из списка желаний
    if Product.objects.filter(favourites=request.user.id).exists():  # добавление в избранное
        fav = True

    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all() # количество товаров в корзине

    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)


    context = {
        'product': product,
        'product_hit': product_hit,
        'product_popular': product_popular,
        'top_discounts': top_discounts,
        'product_new': product_new,
        'product_random': product_random,
        'fav': fav,
        'banner': banner,
        'shop': shop,
        'categories': categories,
        'sliders': sliders,
        'stock': stock,
        'brand_top': brand_top,
        'product_en': product_en
    }

    return render(request, 'index.html', context)



def get_search(request): # Поиск
    if request.method == 'POST':
        searched = request.POST['searched']
        product_search = Product.objects.filter(title__contains=searched, brand__title__contains=searched) # Поиск по title и brand title
        shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине
        categories = Category.objects.all()  # Menu

        return render(request, 'search.html', {'searched': searched, 'product_search': product_search, 'shop': shop, 'categories': categories})
    else:
        categories = Category.objects.all()  # Menu
        return render(request, 'search.html', {'categories': categories})




def get_detail(request, slug:int): # описание товара
    product_detail = get_object_or_404(Product, id=slug)
    query = request.GET.get('q')
    images = Images.objects.filter(product_id=slug) # дополнительные изображения для товара
    product_circle = Product.objects.all()[:6] # Рекомендуем также
    product_popular = Product.objects.all()[:6] # ПОПУЛЯРНЫЕ
    categories = Category.objects.all() # base {% recursetree categories %}

    defaultlang = settings.LANGUAGE_CODE[0:2] #en-EN
    currentlang = request.LANGUAGE_CODE[0:2]


    if defaultlang != currentlang:
        product_en = ProductLangEN.objects.get(product=product_detail) # товар на английском языке
    else:
        product_en = Product.objects.all()



    related_products = Product.objects.filter(category_id=product_detail.category).exclude(id=slug) # Похожие товары

    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)

    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине

    # total = 0 # Подсчёт общей  суммы корзины
    # for rs in shopcart:
    #     total += rs.product.price * rs.quantity

    fav = bool # Добавить в список желаний || Удалите из списка желаний

    if product_detail.favourites.filter(id=request.user.id).exists(): # добавление в избранное
        fav = True

    compare = bool # проверка зарегистрирован пользователи для сравнение

    if product_detail.comparison.filter(id=request.user.id).exists(): # добавление в сравнение
        compare = True

    comments = Comment.objects.filter(product=product_detail).order_by('-create_at') # побликация комментарий
    rate = Comment.objects.all().annotate(username_count=Count('product')).all() # подсчёт количества рейтинга

    if request.method == 'POST': # отправка комметарий
        form = CommentForm(request.POST)
        if form.is_valid():
            user_comment = form.save(commit=False)
            user_comment.product = product_detail
            user_comment.save()
            return HttpResponseRedirect(reverse('detail', args=[slug]))
    else:
        form = CommentForm()


    ip = get_client_ip(request) # счетчик просмотров БЕЗ НАКРУТКИ!

    if Ip.objects.filter(ip=ip).exists():
        product_detail.views.add(Ip.objects.get(ip=ip))
    else:
        Ip.objects.create(ip=ip)
        product_detail.views.add(Ip.objects.get(ip=ip))


    context = {
        'product_detail': product_detail,
        'images': images,
        'fav': fav,
        'shopcart': shopcart,
        'comments': comments,
        'form': form,
        'rate': rate,
        'product_circle': product_circle,
        'product_popular': product_popular,
        'compare': compare,
        'shop': shop,
        'related_products': related_products,
        'categories': categories,
        'product_en': product_en

    }


    if product_detail.variant != "None": # продукт с вариантом
        if request.method == 'POST': # если мы выберем цвет и размеры
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id)
            colors = Variants.objects.filter(product_id=slug,size_id=variant.size_id ) # цвета
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [slug]) # размеры
            query += variant.title+' Size:' +str(variant.size) +' Color:' +str(variant.color) # запрос
        else:
            variants = Variants.objects.filter(product_id=slug)
            colors = Variants.objects.filter(product_id=slug, size_id=variants[0].size_id)
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [slug])
            variant = Variants.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors,
                        'variant': variant,'query': query
                        })

    return render(request, 'product-detail.html', context)



def is_valid_queryparam(param): # параметром запроса для get_category
    return param != '' and param is not None



def get_category(request, category_id): # категории
    product = Product.objects.filter(category_id=category_id) # показ товара на странице
    category = Category.objects.get(pk=category_id)
    categories = Category.objects.all().annotate(posts_count=Count('product')) # отображение категории на странице и также подсчёт товаров в категории
    view_count_min = request.GET.get('view_count_min') # минимальная цена
    view_count_max = request.GET.get('view_count_max') # максимальная цена

    if is_valid_queryparam(view_count_min):
        product = product.filter(price__gte=view_count_min) # минимальная цена

    if is_valid_queryparam(view_count_max):
        product = product.filter(price__lt=view_count_max) # максимальная цена

    category_count = Product.objects.filter(category_id=category_id).annotate(category_count=Count('category')).all() # НАЙДЕНО  {{ category_count.count }}  РЕЗУЛЬТАТОВ

    # new_product = request.GET.get('new_product')
    # latest = request.GET.get('product_name')
    #
    # if new_product == 'new_product':
    #     product = product.filter(title=new_product).order_by('-update_at')
    # elif latest == 'product_name':
    #     product = product.order_by('?') avaregereview

    defaultlang = settings.LANGUAGE_CODE[0:2]  # en-EN
    currentlang = request.LANGUAGE_CODE[0:2]


    if defaultlang != currentlang:
        product_en = ProductLangEN.objects.filter(category_id=category_id) # товар на английском языке
        categories_en = CategoryLangEn.objects.all()  # отображение категории на странице и также подсчёт товаров в категории
    else:
        product_en = Product.objects.filter(category_id=category_id)
        categories_en = CategoryLangEn.objects.all()  # отображение категории на странице и также подсчёт товаров в категории



    sort_by = request.GET.get("sort", "l2h")
    if sort_by == "l2h": # Сортировать По: Самая Низкая Цена
        product = product.order_by("price")
    elif sort_by == "h2l": # Сортировать По: Самая Высокая Цена
        product = product.order_by("-price")
    elif sort_by == "l2hfavourites": # Сортировать По: Лучший Рейтинг
        product = product.order_by('-comments')
    elif sort_by == "h2old": # Сортировать По: Последние Товары
        product = product.order_by('-update_at')
    elif sort_by == "new": # Новейшим Товарам
        product = product.order_by('update_at')



   # Пагинация
    p = Paginator(product, 1) # отображение количества товара на странице
    page_num = request.GET.get('page', 1) # начало показа страницы
    try:
        page = p.page(page_num)
        nums = "a" * page.paginator.num_pages # {% for i in nums %} нумерация страниц
    except EmptyPage:
        return HttpResponse('<h1>Такое страницы нету</h1>')
    # end Пагинация




    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине

    context = {
        'category': category,
        'product': page,
        'shop': shop,
        'categories': categories,
        'category_count': category_count,
        'nums': nums,
        'product_en': product_en,
        'categories_en': categories_en,
    }

    return render(request, 'category.html', context)



def get_brand(request, brand_id): # бренд
    product = Product.objects.filter(brand_id=brand_id)  # показ товара на странице
    brands = Category.objects.get(pk=brand_id)
    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине
    categories = Category.objects.all().annotate(
        posts_count=Count('product'))  # отображение категории на странице и также подсчёт товаров в категории

    view_count_min = request.GET.get('view_count_min')  # минимальная цена
    view_count_max = request.GET.get('view_count_max')  # максимальная цена

    if is_valid_queryparam(view_count_min):
        product = product.filter(price__gte=view_count_min)  # минимальная цена

    if is_valid_queryparam(view_count_max):
        product = product.filter(price__lt=view_count_max)  # максимальная цена

    category_count = Product.objects.filter(brand_id=brand_id).annotate(
        category_count=Count('category')).all()  # НАЙДЕНО  {{ category_count.count }}  РЕЗУЛЬТАТОВ

    sort_by = request.GET.get("sort", "l2h")
    if sort_by == "l2h":  # Сортировать По: Самая Низкая Цена
        product = product.order_by("price")
    elif sort_by == "h2l":  # Сортировать По: Самая Высокая Цена
        product = product.order_by("-price")
    elif sort_by == "l2hfavourites":  # Сортировать По: Лучший Рейтинг
        product = product.order_by('-comments')
    elif sort_by == "h2old":  # Сортировать По: Последние Товары
        product = product.order_by('-update_at')
    elif sort_by == "new":  # Новейшим Товарам
        product = product.order_by('update_at')

    # Пагинация
    p = Paginator(product, 1)  # отображение количества товара на странице
    page_num = request.GET.get('page', 1)  # начало показа страницы
    try:
        page = p.page(page_num)
        nums = "a" * page.paginator.num_pages  # {% for i in nums %} нумерация страниц
    except EmptyPage:
        return HttpResponse('<h1>Такое страницы нету</h1>')
    # end Пагинация

    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине

    context = {
        'brands': brands,
        'product': page,
        'shop': shop,
        'categories': categories,
        'category_count': category_count,
        'nums': nums,
    }

    return render(request, 'brand.html', context)



def compare_list(request): # лист сравнение товара по цене
    compare = Product.objects.filter(comparison=request.user)
    categories = Category.objects.all()  # Menu
    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине
    return render(request,
                  'comparisons.html',
                  {'compare': compare, 'categories': categories, 'shop': shop})




def compare_add(request, id): # добавление сравнение товара по цене
    post = get_object_or_404(Product, id=id)
    if post.comparison.filter(id=request.user.id).exists():
        post.comparison.remove(request.user)
    else:
        post.comparison.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])



class AddLike(LoginRequiredMixin, View):  # лайки к комментариям

    def post(self, request, pk, *args, **kwargs):
        post = Comment.objects.get(pk=pk)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break


        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)

        if is_like:
            post.likes.remove(request.user)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class AddDislike(LoginRequiredMixin, View): # дизлайки к комментариям



    def post(self, request, pk, *args, **kwargs):
        post = Comment.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)



        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])




def get_stock(request): # Страница с акциями
    product_stock = Stock.objects.all()
    categories = Category.objects.all()

    context = {
        'product_stock': product_stock,
        'categories': categories
    }

    return render(request, 'stock.html', context)




def brand_list(request): # список брендов
    categories = Category.objects.all()
    brand = Brand.objects.all()

    context = {
        'categories': categories,
        'brand': brand
    }

    return render(request, 'brand_list.html', context)


def support_chat(request): #  онлайн-чат поддержки
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    return render(request, 'support_chat.html', context)


def contacts(request): # контакты
    categories = Category.objects.all()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'],   form.cleaned_data['content'],
                             'robertdjango23@mail.ru',
                             ['robertdjango23@gmail.com'], fail_silently=True)
            if mail:
                messages.success(request, 'Письмо отправлено!')
                return redirect('contacts')
            else:
                messages.error(request, 'Ошибка отправки')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = ContactForm()

    context = {
        'categories': categories,
        'form': form
    }

    return render(request, 'contacts.html', context)


def selectcurrency(request): # выберите валюту
    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':  # check post
        request.session['currency'] = request.POST['currency']
    return HttpResponseRedirect(lasturl)




