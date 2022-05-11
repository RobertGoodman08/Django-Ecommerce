from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from users.forms import SignUpForm, ProfileUpdateForm, UserUpdateForm
from users.models import UserProfile, CustomerUser
from product.models import Product
from django.conf import settings
from django.core.mail import send_mail
from orders.models import Order, OrderProduct
from product.models import Category, Comment
from orders.models import ShopCart
from django.db.models import Count
import uuid



@login_required(login_url='/login') # Проверьте логин
def index(request): # profile
    current_user = request.user  # Доступ к информации о сеансе пользователя
    profile = UserProfile.objects.get(user_id=current_user.id)
    categories = Category.objects.all()  # Menu
    shop = ShopCart.objects.all().annotate(shop_count=Count('product')).all()  # количество товаров в корзине
    product = Product.objects.filter(favourites=current_user).count() # количество товаров в Избранное
    context = {#'category': category,
               'profile':profile,
               'categories':categories,
                'shop': shop,
                'product': product
    }
    return render(request,'profile/user_profile.html',context)




def logout_func(request): # logout
    logout(request)
    return HttpResponseRedirect('/')



@login_required(login_url='login') # проверка что пользователь зарегистрирован
def favourite_list(request): # лист избранных товаров
    new = Product.objects.filter(favourites=request.user)
    categories = Category.objects.all()  # Menu
    return render(request,
                  'favourites.html',
                  {'new': new, 'categories': categories})



@login_required(login_url='login') # проверка что пользователь зарегистрирован
def favourite_add(request, id): # добавление избранных товаров
    post = get_object_or_404(Product, id=id)
    if post.favourites.filter(id=request.user.id).exists():
        post.favourites.remove(request.user)
    else:
        post.favourites.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])






# --------------------------------------------------------------------------------------


# кому нужна будет сами настроить recaptcha для login и register снизу образец

# def doLogin(request):  для  django-recaptcha 3.0.0
#     if request.method!="POST":
#         return HttpResponse("<h2>Method Not Allowed</h2>")
#     else:
#         captcha_token=request.POST.get("g-recaptcha-response")
#         cap_url="https://www.google.com/recaptcha/api/siteverify"
#         cap_secret="6LeWtqUZAAAAANlv3se4uw5WAg-p0X61CJjHPxKT"
#         cap_data={"secret":cap_secret,"response":captcha_token}
#         cap_server_response=requests.post(url=cap_url,data=cap_data)
#         cap_json=json.loads(cap_server_response.text)
#
#         if cap_json['success']==False:
#             messages.error(request,"Invalid Captcha Try Again")
#             return HttpResponseRedirect("/")
#
#         user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
#         if user!=None:
#             login(request,user)
#             if user.user_type=="1":
#                 return HttpResponseRedirect('/admin_home')
#             elif user.user_type=="2":
#                 return HttpResponseRedirect(reverse("staff_home"))
#             else:
#                 return HttpResponseRedirect(reverse("student_home"))
#         else:
#             messages.error(request,"Invalid Login Details")
#             return HttpResponseRedirect("/")






def login_form(request): # логин
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST.get('password')

        user_obj = CustomerUser.objects.filter(email=email).first()
        if user_obj is None:
            messages.success(request, 'Пользователь не найден.')
            return redirect('/user/login')

        profile_obj = UserProfile.objects.filter(user=user_obj).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Профиль не верифицирован, проверьте свою почту.')
            return redirect('/user/login')

        user = authenticate(request, email=email, password=password)
        if user is None:
            messages.success(request, 'Ошибка входа !! Логин или пароль неверны')
            return redirect('/user/login')

        login(request, user)
        return redirect('/')
    categories = Category.objects.all()  # Menu

    return render(request, 'login.html', {'categories': categories})



def register_form(request): # регистрация
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            print(password)

            try:
                if CustomerUser.objects.filter(email=email).first():
                    messages.success(request, 'Email пользователя занято.')
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])

                if CustomerUser.objects.filter(email=email).first():
                    messages.success(request, 'Электронная почта занята.')
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])

                user_obj = CustomerUser(email=email, username=username, first_name=first_name, last_name=last_name)
                user_obj.set_password(password)
                user_obj.save()
                auth_token = str(uuid.uuid4())
                profile_obj = UserProfile.objects.create(user=user_obj,  auth_token=auth_token)
                profile_obj.save()
                send_mail_after_registration(email, auth_token)
                return redirect('/user/token')

            except Exception as e:
                print(e)
        else:
            messages.warning(request, form.errors)
            return

    form = SignUpForm()
    categories = Category.objects.all()  # Menu
    context = {  # 'category': category,
        'form': form,
        'categories': categories,
    }

    return render(request, 'register.html', context)





def verify(request, auth_token): # проверка почты
    try:
        profile_obj = UserProfile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Ваша учетная запись уже подтверждена.')
                return redirect('/user/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Ваша учетная запись была подтверждена.')
            return redirect('/user/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')


def send_mail_after_registration(email, token): # отправка письма
    subject = 'Ваши учетные записи должны быть проверены'
    message = f'Вставьте ссылку для подтверждения вашей учетной записи http://127.0.0.1:8000/user/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def success(request):
    categories = Category.objects.all()  # Menu
    return render(request , 'success.html', {'categories': categories})


def token_send(request):
    categories = Category.objects.all()  # Menu
    return render(request , 'token_send.html', {'categories': categories})


def error_page(request):
    categories = Category.objects.all()  # Menu
    return  render(request , 'error.html', {'categories': categories})








#
# def send_forget_password(email, token):
#     token = str(uuid.uuid4())
#     subject = 'Your forget password link'
#     message = f'Hi, click on the link to reset your password http://127.0.0.1:8000/change-password/{token}/'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     send_mail(subject, message, email_from, recipient_list)
#
#
#
#
# def forget_password(request):
#     categories = Category.objects.all()  # Menu
#     try:
#         if request.method == 'POST':
#             email = request.POST.get('email')
#
#             if not CustomerUser.objects.filter(email=email).first():
#                 return redirect('register')
#
#             token = str(uuid.uuid4())
#             user_obj = CustomerUser.objects.get(email=email) # change-password
#             send_mail_after_registration(email, token)
#
#     except Exception as e:
#         print(e)
#
#     context = {
#         'categories': categories
#     }
#     return render(request, '')






# -------------------------------------------------------------

@login_required(login_url='/login')
def user_update(request): # обновить данные пользователя
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user) # request.user is user  data
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваша учетная запись была обновлена!')
            return HttpResponseRedirect('/user')
    else:
        category = Category.objects.all()
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile) #"userprofile" model -> OneToOneField relatinon with user
        categories = Category.objects.all()  # Menu
        context = {
            'category': category,
            'user_form': user_form,
            'profile_form': profile_form,
            'categories': categories,
        }
        return render(request, 'profile/user_update.html', context)

@login_required(login_url='/login')
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Ваш пароль был успешно обновлен!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Пожалуйста, исправьте приведенную ниже ошибку..<br>'+ str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        form = PasswordChangeForm(request.user)
        categories = Category.objects.all()  # Menu
        return render(request, 'profile/user_password.html', {'form': form,'categories': categories
                       })



@login_required(login_url='/login')
def user_orders(request):
    current_user = request.user
    orders=Order.objects.filter(user_id=current_user.id)
    categories = Category.objects.all()  # Menu
    context = {'categories': categories,
               'orders': orders,
               }
    return render(request, 'profile/user_orders.html', context)




@login_required(login_url='/login')
def user_orderdetail(request,id):
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    orderitems = OrderProduct.objects.filter(order_id=id)
    categories = Category.objects.all()  # Menu
    context = {
        'categories': categories,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'profile/user_order_detail.html', context)




@login_required(login_url='/login')
def user_order_product(request):
    categories = Category.objects.all()  # Menu
    current_user = request.user
    order_product = OrderProduct.objects.filter(user_id=current_user.id).order_by('-id')
    context = {
                'categories': categories,
               'order_product': order_product,
               }
    return render(request, 'profile/user_order_products.html', context)




@login_required(login_url='/login')
def user_order_product_detail(request,id,oid):
    categories = Category.objects.all()  # Menu
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    orderitems = OrderProduct.objects.filter(id=id,user_id=current_user.id)
    context = {
        'categories': categories,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'profile/user_order_detail.html', context)







@login_required(login_url='/login')
def my_payment_methods(request): # Мои способы оплаты
    current_user = request.user
    profile = UserProfile.objects.get(user_id=current_user.id)
    categories = Category.objects.all()  # Menu
    context = {
        'profile': profile,
        'categories': categories
    }
    return render(request, 'profile/my_payment_methods.html', context)


@login_required(login_url='/login') # Возврат товара и Возврат денежных средств
def my_refunds_and_cancellations(request):
    current_user = request.user
    profile = UserProfile.objects.get(user_id=current_user.id)
    categories = Category.objects.all()  # Menu
    context = {
        'profile': profile,
        'categories': categories
    }
    return render(request, 'profile/my_refunds_and_cancellations.html', context)



#
# def login_form(request): # авторизация пользователя
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             login(request, user)
#             current_user =request.user
#             userprofile=UserProfile.objects.get(user_id=current_user.id)
#             request.session['userimage'] = userprofile.image.url
#             return HttpResponseRedirect('/')
#         else:
#             messages.warning(request,"Ошибка входа !! Логин или пароль неверны")
#             return HttpResponseRedirect(request.META['HTTP_REFERER'])
#
#     return render(request, 'login.html')
#
# def logout_func(request):
#     logout(request)
#     return HttpResponseRedirect('/')
#
#
# def register_form(request): # региситрация пользователя
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save() #completed sign up
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password1')
#             user = authenticate(email=email, password=password)
#             login(request, user)
#             current_user = request.user
#             data=UserProfile()
#             data.user_id=current_user.id
#             data.image="images/users/user.png"
#             data.save()
#             messages.success(request, 'Ваша учетная запись была создана!')
#             return HttpResponseRedirect('/')
#         else:
#             messages.warning(request,form.errors)
#             return HttpResponseRedirect(request.META['HTTP_REFERER'])
#
#
#     form = SignUpForm()
#     #category = Category.objects.all()
#     context = {#'category': category,
#                'form': form,
#                }
#     return render(request, 'register.html', context)
