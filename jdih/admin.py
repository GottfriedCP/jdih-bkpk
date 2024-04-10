from django.contrib import admin
from django.db import models as django_model
from django.forms import CheckboxSelectMultiple
from . import forms, models

admin.site.site_header = "Administrasi Konten JDIH Kemkes"
admin.site.site_title = "JDIH Kemkes"
admin.site.index_title = "Beranda"


# Tidak jadi digunakan
# class CabutInline(admin.TabularInline):
#     model = models.Cabut
#     extra = 1
#     fk_name = "pencabut"


@admin.register(models.Peraturan)
class PeraturanAdmin(admin.ModelAdmin):
    form = forms.PeraturanForm
    list_display = ["kode", "judul", "tahun", "bentuk", "status"]
    filter_horizontal = [
        "subyek",
        "kategori",
        "tema",
        # "mencabuts",  # lihat exclude
        # "mencabut_sebagians",
        # "mengubahs",
        # "melengkapis",
    ]
    # sementara sembunyikan relasi regulasi
    exclude = [
        "mencabuts",
        "mencabut_sebagians",
        "mengubahs",
        "melengkapis",
    ]
    search_fields = ["kode", "judul"]
    # formfield_overrides = {
    #     django_model.ManyToManyField: {"widget": CheckboxSelectMultiple},
    # }
    # inlines = (CabutInline, )


@admin.register(models.BentukPeraturan)
class BentukPeraturanAdmin(admin.ModelAdmin):
    form = forms.BentukPeraturanForm
    list_display = ["nama_lengkap_bentuk", "singkatan_nama_bentuk"]


@admin.register(models.Subyek)
class SubyekAdmin(admin.ModelAdmin):
    list_display = ["judul"]


@admin.register(models.Kategori)
class KategoriAdmin(admin.ModelAdmin):
    form = forms.KategoriForm
    list_display = ["judul", "slug"]


@admin.register(models.Tema)
class TemaAdmin(admin.ModelAdmin):
    form = forms.TemaForm
    list_display = ["judul", "slug"]
