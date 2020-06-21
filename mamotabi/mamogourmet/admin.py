from django.contrib import admin

# Register your models here.
from .models import Category, Pref

admin.site.register(Category)
admin.site.register(Pref)
