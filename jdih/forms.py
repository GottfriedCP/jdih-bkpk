from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import BentukPeraturan, Kategori, Peraturan, Tema


class PeraturanForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean_kode(self):
        kode = self.cleaned_data["kode"]
        duplicate_found = Peraturan.objects.filter(kode=kode).exists()
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Peraturan dengan kode yang sama sudah ada.")
        return kode


class BentukPeraturanForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean_nama_lengkap_bentuk(self):
        nama_lengkap_bentuk = self.cleaned_data["nama_lengkap_bentuk"]
        slug = slugify(nama_lengkap_bentuk)
        duplicate_found = BentukPeraturan.objects.filter(slug=slug).exists()
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Bentuk peraturan ini sudah ada di sistem.")
        return nama_lengkap_bentuk


class KategoriForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean_judul(self):
        judul = self.cleaned_data["judul"]
        slug = slugify(judul)
        duplicate_found = Kategori.objects.filter(slug=slug).exists()
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Kategori peraturan ini sudah ada di sistem.")
        return judul


class TemaForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean(self):
        cleaned_data = super().clean()
        judul = cleaned_data.get("judul")
        slug = cleaned_data.get("slug")
        duplicate_found = (
            Tema.objects.filter(judul=judul).exists()
            or Tema.objects.filter(slug=slug).exists()
        )
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Tema peraturan ini sudah ada di sistem.")
        return cleaned_data
