from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from .models import *

@receiver(m2m_changed, sender=Post.likes.through)
def users_likes_changed(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()

@receiver(post_delete, sender=Post)
def delete_post(sender ,instance, **kwargs):
    author = instance.author
    subject = "Your post has been deleted"
    message = f"Your post has been deleted(Id:{instance.id})"
    send_mail(subject,message,'Arhn84444@gmail.com',[author.email],fail_silently=False)

@receiver(post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        instance.bio = " بایویی ثبت نشده"
        instance.job = " شغلی ثبت نشده"
        instance.save()
