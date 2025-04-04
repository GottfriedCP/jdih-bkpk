import os
import re

from collections import Counter

# import fitz
# import nltk

from django.db.models import F, Q, Count
from django.contrib import messages
from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404

# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

from .models import BentukPeraturan, Peraturan, Subyek, Kategori, Tema


def index(request):
    peraturans = Peraturan.objects.all()
    jumlah_peraturan = peraturans.count()
    peraturans = (
        peraturans.exclude(Q(tanggal_penetapan__isnull=True))
        .filter(status=Peraturan.BERLAKU)
        .order_by("-tanggal_penetapan")[:10]
    )
    bentuk_peraturans = (
        BentukPeraturan.objects
        .order_by("singkatan_nama_bentuk")
        .filter(tayang=True)
        .annotate(peraturans_count=Count("peraturans"))
    )
    return render(
        request,
        "jdih/index.html",
        {
            "jumlah_peraturan": jumlah_peraturan,
            "peraturans": peraturans,
            "bentuks": bentuk_peraturans,
            "beranda": True,
        },
    )


def daftar_peraturan(request):
    # untuk populate kotak pencarian
    bentuk_peraturans = BentukPeraturan.objects.all()
    subyeks = Subyek.objects.all()
    kategoris = Kategori.objects.all()

    keyword = ""
    nomor = ""
    tahun = ""
    bentuk = ""
    ps = Peraturan.objects
    try:
        # BY KEYWORD
        if request.GET.get("keyword"):
            # batasi 30 karakter
            keyword = str(request.GET.get("keyword"))[:30]
            # ps = ps.filter(judul__search=keyword)
            # ps = ps.annotate(
            #     headline=SearchHeadline("teks", SearchQuery(keyword), max_fragments=3)
            # )
            # ps = ps.annotate(search=SearchVector("headline", "judul", "kode"))
            # ps = ps.annotate(search=SearchVector("teks", "judul", "kode"))
            # ps = ps.filter(search=keyword)
            ps = ps.filter(
                Q(teks_vektor=keyword)
                | Q(judul__icontains=keyword)
                | Q(kode__icontains=keyword)
            )
            ps = ps.annotate(
                headline=SearchHeadline("teks", SearchQuery(keyword), max_fragments=3)
            )
        # BY NOMOR
        if request.GET.get("nomor"):
            nomor = request.GET.get("nomor")
            ps = ps.filter(nomor=int(nomor))
        # BY TAHUN
        if request.GET.get("tahun"):
            tahun = request.GET.get("tahun")
            ps = ps.filter(tahun=int(tahun))
        # BY BENTUK PERATURAN
        if request.GET.get("bentuk"):
            bentuk = request.GET.get("bentuk")
            ps = ps.filter(bentuk__id__in=(int(bentuk),))
        ps = ps.all().order_by("-tanggal_penetapan")  # harusnya ada tahun juga

        paginator = Paginator(ps, 7, orphans=5, allow_empty_first_page=True)
        page_number = int(request.GET.get("laman", 1))
        peraturans_p = paginator.get_page(page_number)
        paginator_range = (
            paginator.get_elided_page_range(page_number)
            if paginator.num_pages > 1
            else []
        )
    except:
        return redirect("jdih:daftar_peraturan")

    # Ganti ini dengan
    # bentuk = int(bentuk) if bentuk.isdigit() else ""
    try:
        bentuk = int(bentuk)
    except ValueError:
        bentuk = ""

    context = {
        "keyword": keyword,
        "nomor": nomor,
        "tahun": tahun,
        "bentuk": bentuk,
        "peraturans": peraturans_p,
        "paginator_range": paginator_range,
        "bentuks": bentuk_peraturans,
        "dokumen_hukum": True,
        "subyeks": subyeks,
        "kategoris": kategoris,
        "status_berlaku": Peraturan.BERLAKU,
    }
    return render(request, "jdih/daftar-peraturan.html", context=context)


def detail(request, peraturan_id):
    peraturan_queryset = Peraturan.objects.select_related("bentuk")
    peraturan_queryset = peraturan_queryset.prefetch_related(
        "mencabuts",
        "mencabut_sebagians",
        "mengubahs",
        "melengkapis",
        "subyek",
        "kategori",
        "tema",
    )
    peraturan = get_object_or_404(peraturan_queryset, id=peraturan_id)
    # non-aktifkan jika ada pencabutnya
    if peraturan.pencabuts.exists():
        peraturan.status = Peraturan.TIDAK_BERLAKU
        peraturan.save()
    # cek apakah file PDF regulasi bisa ditemukan di storage
    try:
        dokumen_tersedia = (
            peraturan.file_dokumen != ""
            and peraturan.file_dokumen is not None
            and os.path.isfile(peraturan.file_dokumen.path)
        )
    except:
        dokumen_tersedia = False

    context = {
        "peraturan": peraturan,
        "dokumen_tersedia": dokumen_tersedia,
        "peraturan_is_berlaku": peraturan.status == Peraturan.BERLAKU,
        "dokumen_hukum": True,
    }
    response = render(request, "jdih/detail-peraturan.html", context)
    if not request.COOKIES.get(str(peraturan.id)):
        peraturan.jumlah_lihat = F("jumlah_lihat") + 1
        peraturan.save()
        response.set_cookie(str(peraturan.id), peraturan.judul)
    return response


def unduh(request, peraturan_id):
    file_path = Peraturan.objects.get(id=peraturan_id).file_dokumen.path
    return FileResponse(open(file_path, "rb"))


def cari(request):
    keyword = ""
    nomor = ""
    tahun = ""
    ps = Peraturan.objects
    # BY KEYWORD
    if request.GET.get("keyword"):
        keyword = request.GET.get("keyword")
        # ps = ps.filter(judul__search=keyword)
        ps = ps.annotate(
            headline=SearchHeadline("teks", SearchQuery(keyword), max_fragments=3)
        )
        ps = ps.annotate(search=SearchVector("teks", "judul", "kode"))
        ps = ps.filter(search=keyword)
    # BY NOMOR
    if request.GET.get("nomor"):
        nomor = request.GET.get("nomor")
        ps = ps.filter(nomor=int(nomor))
    # BY TAHUN
    if request.GET.get("tahun"):
        tahun = request.GET.get("tahun")
        ps = ps.filter(tahun=int(tahun))
    # BY BENTUK PERATURAN
    if request.GET.get("bentuk"):
        bentuk = request.GET.get("bentuk")
        ps = ps.filter(bentuk__id__in=(int(bentuk),))
    ps = ps.all()
    context = {
        "dokumen_hukum": True,
        "keyword": keyword,
        "nomor": nomor,
        "tahun": tahun,
        "peraturans": ps,
        "bentuks": BentukPeraturan.objects.all(),
        "subyeks": Subyek.objects.all(),
        "kategoris": Kategori.objects.all(),
        "status_berlaku": Peraturan.BERLAKU,
    }
    return render(request, "jdih/daftar-peraturan.html", context=context)


# def extract_text(request):
#     if request.method == "POST" and request.FILES["try"]:
#         myfile = request.FILES["try"]
#         # print(type(myfile))  # django.core.files.uploadedfile.InMemoryUploadedFile
#         fs = FileSystemStorage()
#         filename_string = re.sub(r"\s+", "", myfile.name)
#         filename = fs.save(f"{filename_string}", myfile)
#         uploaded_file_url = fs.url(filename)
#         print(uploaded_file_url)

#         with fitz.open(uploaded_file_url[1:]) as doc:
#             pymupdf_text = ""
#             for page in doc:
#                 pymupdf_text += page.get_text()
#                 # print(type(page))

#         # Hapus karakter non alfanumerik dan non spasi
#         pymupdf_text = re.sub(r"[^A-Za-z0-9 ]+", "", pymupdf_text)

#         # Membuat token dari teks
#         tokens = word_tokenize(pymupdf_text)  # tidak perlu atur bahasa

#         # Hapus stopword dari teks
#         factory = StopWordRemoverFactory()
#         stopwords = factory.get_stop_words()
#         filtered_text = [word for word in tokens if word.lower() not in stopwords]

#         # Hitung frekuensi tiap kata
#         word_counts = Counter(filtered_text)

#         # DEBUG cetak 10 kata yang paling sering keluar
#         for word, count in word_counts.most_common(10):
#             print(f"{word}: {count}")

#         return render(
#             request,
#             "jdih/extract-text.html",
#             {
#                 "extracted_text": pymupdf_text,
#                 "keywords_count": word_counts.most_common(10),
#             },
#         )

#     return render(request, "jdih/extract-text.html")
