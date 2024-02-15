import datetime
import os

from decouple import config
from django.contrib.postgres.search import SearchVector
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
        ps = (
            Peraturan.objects.filter(teks_vektor__isnull=True)
            .exclude(teks__exact="")
            .exclude(teks__isnull=True)
        )

        for p in ps:
            print(f"Processing {p}...")
            p.teks_vektor = SearchVector(F("teks"))
            p.save()
            print("done")
