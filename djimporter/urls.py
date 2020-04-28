
"""
URL routes definition.

Describe the paths where the views are accesible.
"""
from django.urls import path

from . import views

app_name = 'djimporter'

urlpatterns = [
    path('logs/', views.ListImportsView.as_view(), name='importlog-list'),
    path('logs/<int:pk>/', views.ImportDetailView.as_view(), name='importlog-detail'),
]
