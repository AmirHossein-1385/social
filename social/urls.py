from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
app_name = 'social'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('logout/', views.log_out, name="logout"),
    path('', views.index, name="index"),
    path('register/', views.register, name="register"),
    path('user-edit/',views.user_edit, name="user_edit"),
    path('ticket/', views.ticket, name="ticket"),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url=reverse_lazy('social:password_change_done')), name="password_change"),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name="password_change_done"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html',success_url=reverse_lazy('social:password_reset_done'),email_template_name='registration/password_reset_email.html',), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name="password_reset_done"),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',success_url=reverse_lazy('social:password_reset_complete')), name="password_reset_confirm"),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name="password_reset_complete"),
    path('posts/',views.post_list, name="post_list"),
    path('posts/create-post/', views.create_post, name="create_post"),
    # path('posts/<slug:tag_slug>/',views.post_list, name="post_list_by_tag"),
    path('posts/tag/<slug:tag_slug>/', views.post_list, name="post_list_by_tag"),
    path('posts/detail/<int:id>/', views.post_detail, name="post_detail"),
    path('search/', views.search, name="post_search"),
    path('posts/<post_id>/comment/',views.comment_create,name="comment"),
    path('edit-post/<int:post_id>/',views.edit_post,name="edit_post"),
    path('delete-post/<int:post_id>/',views.delete_post,name="delete_post"),
    path('like-post/', views.like_post, name="like_post"),
    path('save-post/', views.save_post,name="save_post"),
    path('profile/', views.profile, name="profile"),
    path('users/',views.user_list, name="user_list"),
    path('users/<username>/',views.user_detail,name="user_detail"),
    path('follow/<int:user_id>/',views.user_follow,name="follow"),
    path('activity/', views.activity, name="activity"),
    path('posts/<int:post_id>/share/',views.share_post,name="share_post"),
    path('followers/<int:user_id>/',views.show_followers, name="followers"),
    path('following/<int:user_id>/',views.show_following, name="following"),
    path('mytickets/',views.show_tickets, name="show_tickets"),
    path('save-posts/', views.saved_posts, name="saved_posts"),
    path('popular-posts',views.most_popular_posts,name="most_popular_posts"),
]

