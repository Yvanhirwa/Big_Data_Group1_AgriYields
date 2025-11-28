from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),

    # ✅ Redirect homepage → /dashboard/
    path('', lambda request: redirect('dashboard/')),
]
