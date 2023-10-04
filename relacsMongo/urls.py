# relacs/urls.py

from django.urls import include, path
from rest_framework import routers
from . import views

#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #path('', views.getUsers),
    path('compounds/', views.CompoundsView.as_view()),
    path('compound/', views.CompoundView.as_view()),
    path('measurements/', views.MeasurementsView.as_view())
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
