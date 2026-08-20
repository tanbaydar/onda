from django.contrib import admin

from .models import RawIngest, RejectedIngest, SyncRun, TrackedSourcePage


admin.site.register(
    (
        TrackedSourcePage,
        SyncRun,
        RawIngest,
        RejectedIngest,
    )
)
