from django.urls import include, path

urlpatterns = [
    path('', include('gameapp.urls')),
]
