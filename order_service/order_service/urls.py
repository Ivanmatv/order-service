from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/api-token-auth/', auth_views.obtain_auth_token),
    path('api/', include('orders.urls')),
]