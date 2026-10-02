from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import *
from django.contrib.auth.admin import UserAdmin

from .models import Post


# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'phone', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('additional information', {'fields': ('date_of_birth','bio','photo','job','phone')}),
    )

def make_deactivation(modeladmin, request, queryset):
    result = queryset.update(active=False)
    modeladmin.message_user(request, f"{result} Posts were rejected")

make_deactivation.short_description = "رد پست"

def make_activation(modeladmin, request, queryset):
    result = queryset.update(active=True)
    modeladmin.message_user(request, f"{result} Posts were accepted")

make_activation.short_description = "تایید پست"

def unlike(modeladmin, request, queryset):
    count  = queryset.count()
    for post in queryset:
        post.likes.clear()
        post.total_likes = 0
        post.save()

    modeladmin.message_user(request, f"likes removed from {count} posts.")

unlike.short_description = "حذف لایک"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author','description','created']
    ordering = ['-created']
    search_fields = ['description']
    actions = [make_deactivation, make_activation, unlike]


def activation_comments(modeladmin, request, queryset):
    result = queryset.update(active=True)
    if queryset.count() == 1:
        modeladmin.message_user(request, f"{result} comment accepted.")
    else:
        modeladmin.message_user(request, f"{result} comments accepted")

activation_comments.short_description = "تایید کامنت"


def deactivation_comments(modeladmin, request, queryset):
    result = queryset.update(active=False)
    if queryset.count() == 1:
        modeladmin.message_user(request, f"{result} comment accepted.")
    else:
        modeladmin.message_user(request, f"{result} comments accepted")

deactivation_comments.short_description = "رد کامنت"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','body','active','created']
    actions = [activation_comments,deactivation_comments]


admin.site.register(Contact)

@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ['id','user','target','action','created']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name','subject','email','message','reply']

