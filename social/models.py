import os
import uuid
import jdatetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from taggit.managers import TaggableManager
from django.utils import timezone
from django_jalali.db import models as jmodels
from django_resized import ResizedImageField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.

def get_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('account_images/', jdatetime.datetime.now().strftime('%Y/%m'), filename)

def get_upload_image(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('post_images/', jdatetime.datetime.now().strftime('%Y/%m'), filename)


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    bio = models.TextField(null=True, blank=True, verbose_name="بایو")
    photo = models.ImageField(max_length=300,verbose_name="تصویر", upload_to=get_upload_path,null=True, blank=True)
    phone = models.CharField(max_length=11,null=True, blank=True)
    job = models.CharField(max_length=250,null=True, blank=True)
    following = models.ManyToManyField('self', through='Contact', related_name='followers', symmetrical=False)

    def get_absolute_url(self):
        return reverse('social:user_detail', args=[self.username])

class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes =[
            models.Index(fields=['-created'])
        ]
        ordering =['-created']

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"



class Post(models.Model):
    # relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    # data fields
    description = models.TextField(verbose_name="توضیحات")
    # date
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    image = ResizedImageField(upload_to=get_upload_image, blank=True, null=True, verbose_name="عکس",size=[200,200],quality=100,crop=['middle','center'])
    saved_by = models.ManyToManyField(User, related_name="saved_posts",blank=True)
    total_likes = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes'])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('social:post_detail', args=[self.id])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="comments")
    name = models.CharField(max_length=250,verbose_name='Name')
    body = models.TextField(verbose_name='Comment text')
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")
    active = models.BooleanField(default=True,verbose_name='Active')

    class Meta:
        ordering =['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"


    def __str__(self):
        return f"{self.name}: {self.body}"


class UserAction(models.Model):
    ACTION_CHOICES = (
        ('like', 'like'),
        ('unlike', 'unlike'),
        ('follow', 'follow'),
        ('unfollow', 'unfollow'),
        ('save', 'save'),
        ('unsave', 'unsave'),
        ('comment', 'comment'),
        ('view', 'view'),
        ('share', 'share'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "اکشن"
        verbose_name_plural = "اکشن ها"


class Ticket(models.Model):
    SUBJECT_CHOICES = (
        ("پیشنهاد","پیشنهاد"),
        ("انتقاد","انتقاد"),
        ("گزارش","گزارش"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=250)
    message = models.TextField()
    phone = models.CharField(max_length=11,blank=True,null=True)
    subject = models.CharField(choices=SUBJECT_CHOICES, max_length=100)
    email = models.EmailField(null=True, blank=True)
    reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تیکت "
        verbose_name_plural = "تیکت ها"