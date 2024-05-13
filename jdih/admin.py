import fitz

from django.contrib import admin
from django.contrib.postgres.search import SearchVector
from django.db.models import F
from django.utils import timezone

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

    def save_model(self, request, obj, form, change):
        # NOTE ini approach yg aneh wkwk
        # simpan agar file bisa ditemukan jika memang ada
        super().save_model(request, obj, form, change)
        if obj.file_dokumen:
            try:
                with fitz.open(obj.file_dokumen.path) as doc:
                    body_text = ""
                    for page in doc:
                        body_text += page.get_text()
                obj.teks = body_text
                # save agar vektor bisa di generate
                super().save_model(request, obj, form, change)
                obj.teks_vektor = SearchVector("teks")
                obj.last_teks_ingestion = timezone.now()
                obj.teks_ingestion_error_message = None
            except Exception as e:
                obj.teks = None
                obj.teks_vektor = None
                obj.teks_ingestion_error_message = e
                # super().save_model(request, obj, form, change)
            super().save_model(request, obj, form, change)

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     qs = qs.prefetch_related("mencabuts")
    #     return qs

    list_display = ["kode", "judul", "tahun", "bentuk", "status"]
    filter_horizontal = [
        "subyek",
        "kategori",
        "tema",
        "mencabuts",  # lihat exclude
        # "mencabut_sebagians",
        # "mengubahs",
        # "melengkapis",
    ]
    # sementara sembunyikan relasi regulasi
    exclude = [
        # "mencabuts",
        "mencabut_sebagians",
        "mengubahs",
        "melengkapis",
    ]
    search_fields = ["kode_judul"]  # ["kode", "judul"]
    autocomplete_fields = ["mencabuts"]
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
