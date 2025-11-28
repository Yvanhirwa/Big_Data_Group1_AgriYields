# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('upload/', views.upload_and_run, name='upload_and_run'),
    path('results/', views.upload_and_run, name='results'),  # results shown after upload
    path('predict/', views.predict_view, name='predict'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]
