from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Document, MLModel

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Document)
admin.site.register(MLModel)
