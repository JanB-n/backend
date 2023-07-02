# relacs/urls.py

from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from . import views

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #path('', views.getUsers),
    path('auth/register/', views.Register.as_view(), name='register'),
    #path('auth/login/', include('rest_framework.urls', namespace='rest_framework'))
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh-token/', TokenRefreshView.as_view(), name='refreshtoken'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
]
