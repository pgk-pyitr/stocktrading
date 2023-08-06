from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/', views.portfolio, name='portfolio'),
    path('buy/<str:symbol>/<int:quantity>/', views.buy_stock, name='buy_stock'),
    path('sell/<str:symbol>/<int:quantity>/', views.sell_stock, name='sell_stock'),
    path('chart/<str:symbol>/', views.show_chart, name='show_chart'),
]
