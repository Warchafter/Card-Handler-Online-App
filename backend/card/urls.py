from django.urls import path, include
from card import views
from rest_framework.routers import DefaultRouter


app_name = 'card'

router = DefaultRouter()
router.register('cards', views.CardViewSet)
router.register('cagetories', views.CardCategoryViewSet)
router.register('colors', views.CardColorViewSet)
router.register('status', views.CardStatusViewSet)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
]
