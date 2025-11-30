# dashboard/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('upload/', views.upload_and_run, name='upload_and_run'),
    path('results/<int:analysis_id>/', views.results_view, name='results'),
    path('results/', views.results_view, name='results_latest'),
    path('predict/', views.predict_view, name='predict'),
    path('export-pdf/<int:analysis_id>/', views.export_pdf, name='export_pdf'),
    path('export-pdf/', views.export_pdf, name='export_pdf_latest'),
    path('history/', views.dataset_history, name='history'),
    path('delete/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),

    # Auth - use custom views instead of Django's generic views
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_redirect_view, name='login'),  # redirect to dashboard (modal shows)
    path('logout/', views.logout_view, name='logout'),

    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='dashboard/password_reset.html',
             email_template_name='dashboard/password_reset_email.html',
             subject_template_name='dashboard/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'),
         name='password_reset_complete'),
]
