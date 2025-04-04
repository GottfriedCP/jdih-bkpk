import datetime
import uuid

from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.text import slugify

from .custom_fields import ContentTypeRestrictedFileField


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Peraturan(TimeStampedModel):
    """Model repr peraturan (dokumen hukum)."""

    BAHASA_CHOICES = (
        ("indonesia", "Bahasa Indonesia"),
        ("inggris", "Bahasa Inggris"),
    )

    BERLAKU = "berlaku"
    TIDAK_BERLAKU = "tidak_berlaku"
    STATUS_CHOICES = ((BERLAKU, "Berlaku"), (TIDAK_BERLAKU, "Tidak Berlaku"))

    DICABUT = "dicabut"
    DICABUT_SEBAGIAN = "dicabut_sebagian"
    DIUBAH = "diubah"
    DILENGKAPI = "dilengkapi"
    LAINNYA = "lainnya"
    ALASAN_TIDAK_BERLAKU_CHOICES = (
        (DICABUT, "Dicabut"),
        (DICABUT_SEBAGIAN, "Dicabut sebagian"),
        (DIUBAH, "Diubah"),
        (DILENGKAPI, "Dilengkapi"),
        (LAINNYA, "Lainnya"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # kode: HK.01.07/MENKES/1134/2022 etc..
    ht_kode = "Misalnya: HK.01.07/MENKES/123/2024"
    kode = models.CharField(
        max_length=150, unique=True, verbose_name="kode peraturan", help_text=ht_kode
    )
    judul = models.CharField(
        max_length=300,
        help_text="Misalnya: Jam Kerja Pegawai di Lingkungan Kementerian Kesehatan Selama Bulan Ramadhan",
    )
    # kode + judul
    kode_judul = models.CharField(max_length=500, null=True, blank=True, editable=False)
    # bentuk: UUD, Tap MPR, fk
    bentuk = models.ForeignKey(
        "BentukPeraturan",
        related_name="peraturans",
        verbose_name="bentuk peraturan",
        on_delete=models.CASCADE,
    )
    nomor = models.IntegerField(blank=True, null=True)
    tahun = models.IntegerField(default=datetime.datetime.now().year)
    unit_eselon_1_pemrakarsa = models.CharField(
        verbose_name="eselon 1 pemrakarsa", max_length=150, blank=True, null=True
    )
    tempat_penetapan = models.CharField(max_length=100, blank=True, null=True)
    tanggal_penetapan = models.DateField(blank=True, null=True)
    tanggal_pengundangan = models.DateField(blank=True, null=True)
    tanggal_berlaku_efektif = models.DateField(blank=True, null=True)
    # lokasi dokumen fisik, contoh Biro Hukum
    lokasi = models.CharField(
        max_length=100, help_text="contoh: Biro Hukum", blank=True, null=True
    )
    # sumber: berita negara (BN) nomor sekian..
    sumber = models.CharField(
        max_length=100, help_text="contoh: BN nomor sekian", blank=True, null=True
    )
    bahasa = models.CharField(
        max_length=20, choices=BAHASA_CHOICES, blank=True, null=True
    )
    # bid_huk: Hukum Keuangan Negara
    bidang_hukum = models.CharField(
        max_length=100, help_text="contoh: Hukum Keuangan Negara", blank=True, null=True
    )
    # subyek (tag) m2m
    subyek = models.ManyToManyField(
        "Subyek", blank=True, verbose_name="subyek atau tag"
    )
    kategori = models.ManyToManyField("Kategori", blank=True)
    # tema: BMN, Covid-19, etc. m2m
    tema = models.ManyToManyField("Tema", blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=BERLAKU)
    alasan_tidak_berlaku = models.CharField(
        max_length=50, choices=ALASAN_TIDAK_BERLAKU_CHOICES, null=True, blank=True
    )

    mencabuts = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
        related_name="pencabuts",
        verbose_name="mencabut",
    )
    mencabut_sebagians = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
        related_name="pencabut_sebagians",
        verbose_name="mencabut sebagian",
    )
    mengubahs = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
        related_name="pengubahs",
        verbose_name="mengubah/melengkapi",
    )
    melengkapis = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
        related_name="pelengkaps",
        verbose_name="melengkapi",
    )

    # Teks hasil ektraksi PDF peraturan
    teks = models.TextField(blank=True, null=True, editable=False)
    teks_vektor = SearchVectorField(blank=True, null=True, editable=False)
    last_teks_ingestion = models.DateTimeField(blank=True, null=True, editable=False)
    teks_ingestion_error_message = models.TextField(
        blank=True, null=True, editable=False
    )
    file_dokumen = ContentTypeRestrictedFileField(
        upload_to="dokumen_hukum/",
        blank=True,
        null=True,
        content_types=["application/pdf"],
        max_upload_size=30 * 1024 * 1024,
    )
    jumlah_lihat = models.IntegerField(default=0, editable=False)
    jumlah_unduh = models.IntegerField(default=0, editable=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "peraturan"
        indexes = [
            models.Index(fields=["kode_judul"]),
            # GinIndex(
            #     name="peraturan_gin_idx",
            #     fields=["teks", "judul", "kode"],
            # )
        ]

    def save(self, *args, **kwargs):
        self.kode_judul = f"{self.kode} {self.judul}"
        super().save(*args, **kwargs)

    def __str__(self):
        # if len(self.judul) > 20:
        #     return f"{self.kode} {str(self.judul)[:20]}"
        # else:
        #     return f"{self.kode} {self.judul}"
        return f"{self.kode} {self.judul}"


# class Cabut(TimeStampedModel):
#     pencabut = models.ForeignKey(
#         "Peraturan", on_delete=models.CASCADE, related_name="to_peraturans"
#     )
#     tercabut = models.ForeignKey(
#         "Peraturan",
#         on_delete=models.CASCADE,
#         related_name="from_peraturans",
#         verbose_name="peraturan tercabut",
#     )

#     def __str__(self):
#         return str(self.tercabut)

#     class Meta:
#         verbose_name = "Mencabut Peraturan"
#         verbose_name_plural = "Mencabut Peraturan"
#         ordering = ("updated_at",)
#         constraints = [
#             models.UniqueConstraint(
#                 name="%(app_label)s_%(class)s_unique_relationships",
#                 fields=["pencabut", "tercabut"],
#             ),
#             models.CheckConstraint(
#                 name="%(app_label)s_%(class)s_cegah_self_cabut",
#                 check=~models.Q(pencabut=models.F("tercabut")),
#             ),
#         ]


class BentukPeraturan(TimeStampedModel):
    """Model repr bentuk peraturan e.g. UUD, KMK"""

    nama_lengkap_bentuk = models.CharField(
        max_length=100,
        verbose_name="nama bentuk peraturan",
        help_text="contoh: Peraturan Presiden",
    )
    # slug untuk memastikan tidak ada nama yang sama
    slug = models.CharField(max_length=100, default="", editable=False, unique=True)
    singkatan_nama_bentuk = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="singkatan",
        help_text="contoh: PP",
    )
    # field bool utk menandai apakah dia tayang di home
    tayang = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.singkatan_nama_bentuk:
            new_string = ""
            words = self.nama_lengkap_bentuk.split()

            for word in words:
                new_string += word[0].upper()
            self.singkatan_nama_bentuk = new_string
        self.slug = slugify(self.nama_lengkap_bentuk)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_lengkap_bentuk} ({self.singkatan_nama_bentuk})"

    class Meta:
        verbose_name_plural = "bentuk peraturan"


class Subyek(TimeStampedModel):
    """Model repr subyek (tag) peraturan/dokumen hukum."""

    judul = models.CharField(
        max_length=50, unique=True, help_text="judul subyek atau tag"
    )

    def save(self, *args, **kwargs):
        if self.judul:
            self.judul = self.judul.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "subyek"


class Kategori(TimeStampedModel):
    """Model repr kategori."""

    judul = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(default="", editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "kategori"


class Tema(TimeStampedModel):
    """Model repr tematik."""

    judul = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(default="", editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "tema"
