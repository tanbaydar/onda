from django.db import models


class Source(models.TextChoices):
    RA = "ra", "Resident Advisor"


class SyncRunType(models.TextChoices):
    NIGHTLY = "nightly", "Nightly"
    BACKFILL = "backfill", "Backfill"
    REPLAY = "replay", "Replay"


class SyncRunStatus(models.TextChoices):
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    CRASHED = "crashed", "Crashed"


class RawProcessingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSED = "processed", "Processed"
    FAILED = "failed", "Failed"


class RejectionReason(models.TextChoices):
    OUT_OF_SCOPE = "OUT_OF_SCOPE", "Out of scope"
    NO_ARTIST = "NO_ARTIST", "No artist"
    EMPTY_TITLE = "EMPTY_TITLE", "Empty title"
    BAD_DATE = "BAD_DATE", "Bad date"
    PARSE_FAILURE = "PARSE_FAILURE", "Event-level parse failure"


class TrackedSourcePage(models.Model):
    source = models.CharField(max_length=50, choices=Source)
    area_ref = models.CharField(max_length=255)
    label = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "TRACKED_SOURCE_PAGE"
        constraints = [
            models.UniqueConstraint(
                fields=("source", "area_ref"),
                name="uq_tracked_source_area",
            ),
        ]


class SyncRun(models.Model):
    run_type = models.CharField(max_length=20, choices=SyncRunType)
    status = models.CharField(max_length=20, choices=SyncRunStatus)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    seeds_attempted = models.IntegerField(default=0)
    seeds_failed = models.IntegerField(default=0)
    events_upserted = models.IntegerField(default=0)
    events_quarantined = models.IntegerField(default=0)
    events_dropped = models.IntegerField(default=0)
    error_summary = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "SYNC_RUN"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(run_type__in=SyncRunType.values),
                name="ck_sync_run_type",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=SyncRunStatus.values),
                name="ck_sync_run_status",
            ),
        ]


class RawIngest(models.Model):
    seed = models.ForeignKey(
        TrackedSourcePage,
        db_column="seed_id",
        db_index=False,
        on_delete=models.RESTRICT,
        related_name="raw_ingests",
    )
    run = models.ForeignKey(
        SyncRun,
        db_column="run_id",
        db_index=False,
        on_delete=models.RESTRICT,
        related_name="raw_ingests",
    )
    window_start = models.DateField(null=True, blank=True)
    window_end = models.DateField(null=True, blank=True)
    page_number = models.IntegerField()
    page_size = models.IntegerField()
    response_body = models.TextField(null=True, blank=True)
    http_status = models.SmallIntegerField(null=True, blank=True)
    fetched_at = models.DateTimeField()
    processing_status = models.CharField(
        max_length=20,
        choices=RawProcessingStatus,
        default=RawProcessingStatus.PENDING,
    )

    class Meta:
        db_table = "RAW_INGEST"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    processing_status__in=RawProcessingStatus.values
                ),
                name="ck_raw_processing_status",
            ),
        ]
        indexes = [
            models.Index(fields=("run",), name="ix_raw_ingest_run"),
            models.Index(
                fields=("seed", "fetched_at"),
                name="ix_raw_ingest_seed_fetched",
            ),
        ]


class RejectedIngest(models.Model):
    raw_ingest = models.ForeignKey(
        RawIngest,
        db_column="raw_ingest_id",
        db_index=False,
        on_delete=models.RESTRICT,
        related_name="rejections",
    )
    entity_ref = models.CharField(max_length=255)
    reason = models.CharField(max_length=30, choices=RejectionReason)
    detail = models.TextField(null=True, blank=True)
    rejected_at = models.DateTimeField()

    class Meta:
        db_table = "REJECTED_INGEST"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(reason__in=RejectionReason.values),
                name="ck_rejection_reason",
            ),
            models.UniqueConstraint(
                fields=("raw_ingest", "entity_ref"),
                name="uq_rejection_payload_entity",
            ),
        ]
