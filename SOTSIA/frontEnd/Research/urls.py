from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('testing/', views.testing, name='testing'),
    path('dataset/', views.dataset, name='dataset'),
    path('reports/', views.reports, name='reports'),
    path('data-mining/', views.algorithm, name='data-mining'),
    path('deep-learning/', views.algorithm, name='deep-learning'),
    path('machine-learning/', views.algorithm, name='machine-learning'),
]
