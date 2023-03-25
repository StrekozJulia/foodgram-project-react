from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

from .views import CustomUserViewSet
                        # SignUp,
#                     TitleViewSet, UsersViewSet, ReviewViewSet, CommentViewSet)


app_name = 'api'

router = DefaultRouter()

# router_v1.register('titles', TitleViewSet, basename='titles')
# router_v1.register('categories', CategoryViewSet, basename='categories')
# router_v1.register('genres', GenreViewSet, basename='genres')
router.register('users', CustomUserViewSet, basename='users')
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )

urlpatterns = [
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', TokenCreateView.as_view(), name="login"),
    # path('auth/token/logout/', TokenDestroyView.as_view(), name="logout"),
    # path('auth/token/', TokenCreateView.as_view(), name='login'),
    # path('auth/signup/', SignUp.as_view(), name='signup'),
    path('', include(router.urls)),
]