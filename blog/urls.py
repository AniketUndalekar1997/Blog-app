from django.urls import path
from blog import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home),
    path('search/', views.search,name='search'),

    path('about/', views.about, name='about'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('addpost/', views.add_post, name='addpost'),
    path('updatepost/<int:id>/', views.update_post, name='updatepost'),
    path('deletepost/<int:id>/', views.delete_post, name='deletepost'),
    path('liked/', views.like_unlike_post, name='like_post'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
