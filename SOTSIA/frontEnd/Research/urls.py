from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('research/', views.research, name='research'),
    path('dataset/', views.dataset, name='dataset'),
    path('reports/', views.reports, name='reports'),
    path('data-mining/', views.algorithm, name='data-mining'),
    path('data-mining/experimentation', views.experimentation, name='data-mining-experimentation'),
    path('deep-learning/', views.algorithm, name='deep-learning'),
    path('deep-learning/experimentation', views.experimentation, name='deep-learning-experimentation'),
    path('machine-learning/', views.algorithm, name='machine-learning'),
    path('machine-learning/experimentation', views.experimentation, name='machine-learning-experimentation'),
    path('reports/<int:id>/', views.document, name='document'),
    path('reports/<int:id>/pdf', views.generate_pdf, name='generate-pdf'),
]
