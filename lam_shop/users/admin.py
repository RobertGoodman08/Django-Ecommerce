from django.contrib import admin
from users.models import  CustomerUser, UserProfile



admin.site.register(CustomerUser)
admin.site.register(UserProfile)