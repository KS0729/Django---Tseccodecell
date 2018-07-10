from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('settings/', views.settings, name='settings'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('challenge/',views.ChallengeListView.as_view(), name='challenges'),
    path('challenge/<int:challenge_id>/', views.challenge, name='challenge_detail'),
    path('user/<int:user_id>',views.user_detail, name='user_detail'),
    path('ranklist/',views.ranklist, name='ranklist'),
    path('challenge/<int:challenge_id>/solutions', views.challenge_ranklist, name='challenge_ranklist'),
    path('about/',views.about, name='about'),
    path('privacypolicy/',views.privacypolicy, name='privacypolicy'),
]
