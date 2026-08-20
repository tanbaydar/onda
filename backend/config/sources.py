from django.db import models


class Source(models.TextChoices):
    RA = "ra", "Resident Advisor"
