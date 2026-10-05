from django.urls import path

from . import views

urlpatterns = [
    path('', views.page('index.html'), name='home'),
    path('login', views.page('login.html'), name='login'),
    path('register', views.page('register.html'), name='register'),
    path('game', views.page('game.html'), name='game'),
    path('admin', views.page('admin.html'), name='admin'),

    path('api/auth/register', views.auth_register, name='api_register'),
    path('api/auth/login', views.auth_login, name='api_login'),
    path('api/game/status', views.game_status, name='api_game_status'),
    path('api/game/start', views.game_start, name='api_game_start'),
    path('api/game/<int:game_id>', views.game_get, name='api_game_get'),
    path('api/game/<int:game_id>/guess', views.game_guess, name='api_game_guess'),
    path('api/admin/reports/day', views.admin_day_report, name='api_day_report'),
    path('api/admin/reports/user/<str:username>', views.admin_user_report, name='api_user_report'),
    path('api/admin/words', views.admin_words, name='api_words'),
    path('api/admin/words/<int:word_id>', views.admin_delete_word, name='api_delete_word'),
]
