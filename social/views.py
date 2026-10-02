from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from social.forms import *
from .models import *
from taggit.models import Tag
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib import messages
from urllib.parse import quote

from .models import Ticket


# Create your views here.


def log_out(request):
    logout(request)
    return redirect('social:index')

def index(request):
    posts = Post.objects.all()
    suggested_users = User.objects.exclude(id=request.user.id)[:5]
    popular_tags = Tag.objects.all()[:10]
    context = {
        'posts': posts,
        'suggested_users': suggested_users,
        'popular_tags': popular_tags,
    }
    return render(request, 'social/index.html',context)


def profile(request):
    user = request.user
    saved_posts = user.saved_posts.all()
    followers = user.followers.all()
    following = user.following.all()
    context = {
        'saved_posts': saved_posts,
        'followers': followers,
        'following': following,
    }
    return render(request, 'social/profile.html',context)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return render(request, 'registration/register_done.html')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {"form": form})


@login_required
def user_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            return redirect('social:index')
    else:
        user_form = UserEditForm(instance=request.user)
    context = {
       "user_form": user_form,
    }
    return render(request,'registration/user_edit.html',context)


# def ticket(request):
#     if request.method == "POST":
#         form = TicketForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             message =f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n\n{cd['message']}"
#             send_mail(cd['subject'], message,"Arhn84444@gmail.com",['Arhn85555@gmail.com'], fail_silently=False)
#             messages.success(request, "ایمیل شما با موفقیت ارسال شد")
#     else:
#         form = TicketForm()
#     context = {
#         "form": form,
#     }
#     return render(request, "forms/Ticket.html", context)

def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_info = form.save(commit=False)
            ticket_info.user = request.user
            ticket_info.save()
            message = (
                f"{ticket_info.name}\n"
                f"{ticket_info.phone}\n"
                f"{ticket_info.email}\n"
                f"{ticket_info.message}\n"
            )
            send_mail(ticket_info.subject,message, "Arhn84444@gmail.com",["Arhn85555@gmail.com"], fail_silently=False)
            return redirect("social:index")

    else:
        form = TicketForm()

    context = {
        "form":form
    }
    return render(request, "forms/ticket.html",context)


def post_list(request,tag_slug=None):
    # posts = Post.objects.all()
    posts = Post.objects.select_related('author').order_by('-total_likes','id').all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    page = request.GET.get('page')
    paginator = Paginator(posts, 2)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = []
    except PageNotAnInteger:
        posts = paginator.page(1)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/list_ajax.html',{'posts':posts})
    context = {
        "posts": posts,
        "tag":tag,
    }
    return render(request, "social/list.html", context)


def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('social:index')

    else:
        form = CreatePostForm()
    context = {
        "form": form,
    }
    return render(request, 'forms/create_post.html',context)

def edit_post(request,post_id):
    post = get_object_or_404(Post,id=post_id)
    if request.method == "POST":
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('social:post_list')

    else:
        form = EditPostForm(instance=post)
    context = {
        "form": form,
        "post": post,
    }
    return render(request, 'forms/edit_post.html',context)


def delete_post(request,post_id):
    post = get_object_or_404(Post,id=post_id)
    if request.method == 'POST':
        if post.author == request.user:
            post.delete()
            return redirect('social:post_list')
        else:
            messages.error(request, "شما اجازه حذف این پست رو ندارید")

    context = {
        'post':post
    }
    return render(request,'forms/delete_post.html',context)


@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)

    UserAction.objects.create(
        user=request.user,
        target=post,
        action='view'
    )

    post_tags_ids = post.tags.values_list('id', flat=True)
    form = CommentForm()
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(some_tags=Count('tags',filter =Q(tags__in=post_tags_ids))).order_by('-some_tags')[:2]
    active_comments = post.comments.filter(active=True)
    context = {
        "post": post,
        "similar_posts": similar_posts,
        "form": form,
        "active_comments": active_comments,
    }
    return render(request, "social/detail.html", context)


def search(request):
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            result = Post.objects.annotate(similarity=TrigramSimilarity('description',query)).filter(similarity__gt=0.1).order_by('-similarity')
    else:
        form = SearchForm()
    context = {
        "form": form,
        "result": result
    }
    return render(request,'social/search.html',context)


# def comment_create(request,post_id):
#     post = get_object_or_404(Post,id=post_id)
#     comment = None
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.save()
#             messages.success(request, "کامنت شما با موفقیت ارسال شد")
#             return redirect('social:post_detail', post.id)
#     else:
#         form = CommentForm()
#     context = {
#         "post": post,
#         "form": form,
#         "comment": comment
#     }
#     return render(request,'partials/comment.html',context)


def comment_create(request,post_id):
    post = get_object_or_404(Post,id=post_id)
    comment = None
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            message = "کامنت شما با موفقیت ارسال شد"
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            UserAction.objects.create(
                user=request.user,
                target=comment,
                action='comment'
            )

            return JsonResponse({"text":comment.body, "message":message})


    return JsonResponse({"errors": "Invalid request"})


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post,id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
            action = 'unlike'
        else:
            post.likes.add(user)
            liked = True
            action = 'like'

        UserAction.objects.create(
            user=user,
            target=post,
            action=action
        )

        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        }
    else:
        response_data = {"error": 'Invalid post id'}

    return JsonResponse(response_data)

@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post,id=post_id)
        user = request.user
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
            action = 'unsave'
        else:
            post.saved_by.add(user)
            saved = True
            action = 'save'

        UserAction.objects.create(
            user=user,
            target=post,
            action=action
        )

        return JsonResponse({"saved":saved})

    return JsonResponse({"error": 'Invalid request'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True).all()
    return render(request, 'user/user_list.html',{'users':users})

@login_required
def user_detail(request,username):
    user = get_object_or_404(User,username=username)
    return render(request,'user/user_detail.html',{'user':user})

@login_required
@require_POST
def user_follow(request,user_id):
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                return JsonResponse({'You cant follow yourself'})
            if user in request.user.following.all():
                Contact.objects.filter(user_from=request.user,user_to=user).delete()
                follow = False
                action = 'unfollow'
            else:
                Contact.objects.get_or_create(user_from=request.user,user_to=user)
                follow = True
                action = 'follow'

            UserAction.objects.create(
                user=request.user,
                target=user,
                action=action
            )

            following_count = user.following.count()
            followers_count = user.followers.count()
            return JsonResponse({'follow':follow,'following_count':following_count,'followers_count':followers_count})

        except User.DoesNotExist:
            return JsonResponse({'error':'User does not exist'})

    return JsonResponse({'error':'Invalid request'})



def activity(request):
    last_24_hours = timezone.now() - timedelta(hours=24)
    actions = UserAction.objects.filter(
        user=request.user,
        created__gte=last_24_hours
    )
    return render(request, 'user/activity.html', {'actions': actions})


@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    UserAction.objects.create(
        user=request.user,
        target=post,
        action='share'
    )

    url = request.build_absolute_uri(post.get_absolute_url())
    text = "!این پست رو ببین"

    telegram_url = f"https://t.me/share/url?url={quote(url)}&text={quote(text)}"

    return redirect(telegram_url)

def show_followers(request,user_id):
    user = get_object_or_404(User, id=user_id)
    followers = user.followers.all()
    return render(request, 'user/followers.html',{'followers':followers})


def show_following(request,user_id):
    user = get_object_or_404(User, id=user_id)
    following = user.following.all()
    return render(request, 'user/following.html',{'following':following})


def show_tickets(request):
    tickets = Ticket.objects.filter(user= request.user)
    return render(request, 'user/tickets.html',{'tickets':tickets})


def saved_posts(request):
    user = request.user
    save = user.saved_posts.all()
    return render(request, 'user/saved_posts.html',{'save':save})


def most_popular_posts(request):
    posts = Post.objects.order_by('-total_likes').all()
    return render(request,'partials/popular_posts.html',{'posts':posts})
