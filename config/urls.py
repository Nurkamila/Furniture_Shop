from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from furniture.views import ProductViewSet, CommentViewSet, CategoryViewSet, toggle_like
from rest_framework import routers
from django.contrib import admin
from django.urls import path, include


schema_view = get_schema_view(
    openapi.Info(
        title='FULLSTACK',
        default_version='v1',
        description='chto=to',
    ),
    public=True
)

router = routers.SimpleRouter()
router.register('products', ProductViewSet)
router.register('category', CategoryViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0)),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/account/', include('account.urls')),
    path('api/v1/products/<int:id>/toggle_like/', toggle_like),
    path('api/v1/export/', include('furniture.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)