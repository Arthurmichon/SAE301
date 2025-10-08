from django.urls import path
from . import views



urlpatterns = [

    path('etat/', views.etat_prise_api, name='etat_prise_api'),
    path('prise/<int:prise_id>/<str:etat>/', views.set_prise_state, name='set_prise_state'),
    path('', views.page_accueil, name='page_accueil'),
    path('debug/check_plages/', views.debug_check_plages, name='debug_check_plages'),
    path('prise/<int:prise_id>/set_prise_state/<str:etat>/', views.set_prise_state, name='set_prise_state'),
    path('prise/<int:prise_id>/set_horaire/', views.set_horaire, name='set_horaire'),
    path('temperature-api/', views.temperature_api, name='temperature_api'),
    path('toggle_all_leds/', views.toggle_all_leds, name='toggle_all_leds'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),



]



