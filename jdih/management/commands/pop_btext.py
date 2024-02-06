import datetime
import os

from decouple import config
from django.core.management.base import BaseCommand
from django.db.models import F, Q
from django.utils import timezone

import fitz

from jdih.models import Peraturan


class Command(BaseCommand):
    help = "Populate the text field of a Peraturan."

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        # ps = Peraturan.objects.filter(
        #     Q(last_teks_ingestion__isnull=True)
        #     | Q(last_teks_ingestion__lt=F("updated_at"))
        # )
        ps = Peraturan.objects.filter(last_teks_ingestion__isnull=True).exclude(file_dokumen__exact="")

        for p in ps:
            if p.file_dokumen is not None and os.path.isfile(p.file_dokumen.path):
                with fitz.open(p.file_dokumen.path) as doc:
                    body_text = ""
                    for page in doc:
                        body_text += page.get_text()
                p.teks = body_text
                p.last_teks_ingestion = timezone.now()
                p.save()
