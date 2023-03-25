from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('', include('recipes.urls', namespace='recipes')),
    # path('auth/', include('users.urls', namespace='users')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
