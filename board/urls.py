from django.urls import path

from . import views

app_name = 'board'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.create_confession, name='create'),
    path('c/<uuid:pk>/', views.detail, name='detail'),
    path('c/<uuid:pk>/like/', views.like_confession, name='like'),
]
