from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from currencies.models import Currency


class CustomerUserManager(BaseUserManager):


    def _create_user(self, email, password,  username,first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("Email не указан")

        if not password:
            raise ValueError("Пароль не указан")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, email, password,  username,first_name, last_name,  **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password,  username, first_name, last_name, **extra_fields)


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', 'admin')

        if extra_fields.get("is_staff") is not True:
            return ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            return ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)



class CustomerUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=240) # имя
    last_name = models.CharField(max_length=240)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)



    objects = CustomerUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def __str__(self):
        return self.email




class UserProfile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(blank=True, max_length=20)
    address = models.CharField(blank=True, max_length=150)
    city = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=50)
    image = models.ImageField(blank=True, upload_to='images/users/')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.user.email

    def user_name(self):
        return self.user.first_name + ' ' + self.user.last_name + ' [' + self.user.username + '] '
