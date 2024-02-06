from django.urls import path

from jdih import views

app_name = "jdih"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<uuid:peraturan_id>/", views.detail, name="detail"),
    path("detail/<uuid:peraturan_id>/unduh/", views.unduh, name="unduh"),
    path("daftar-peraturan/", views.daftar_peraturan, name="daftar_peraturan"),
    path("cari/", views.cari, name="cari"),
]
