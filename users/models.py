from decimal import Decimal

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from zoneinfo import ZoneInfo


username_validator = RegexValidator(
    regex=r"^(?!.*\.\.)[a-z0-9][a-z0-9_.]{1,28}[a-z0-9]$",
    message=(
        "Username must be 3–30 characters using letters, numbers, underscores, "
        "or periods; it must begin and end with a letter or number and cannot "
        "contain consecutive periods."
    ),
)


class DancedUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email).lower()
        username = extra_fields.get("username")
        if username:
            extra_fields["username"] = username.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DEACTIVATED = "deactivated", "Deactivated"
    PENDING_DELETION = "pending_deletion", "Pending deletion"


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        validators=(username_validator,),
    )
    recovery_username = models.CharField(max_length=30, null=True, blank=True)
    display_name = models.CharField(max_length=50)
    bio = models.CharField(max_length=150, null=True, blank=True)
    avatar = models.URLField(max_length=2048, null=True, blank=True)
    home_city = models.ForeignKey(
        "catalog.City",
        db_column="home_city_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_private = models.BooleanField()
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    deletion_due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DancedUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "display_name", "is_private"]

    class Meta:
        db_table = "DANCED_USER"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(status=UserStatus.ACTIVE, username__isnull=False)
                    | Q(
                        status__in=(
                            UserStatus.DEACTIVATED,
                            UserStatus.PENDING_DELETION,
                        ),
                        username__isnull=True,
                    )
                ),
                name="ck_user_status_username",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        status=UserStatus.PENDING_DELETION,
                        deletion_due_at__isnull=False,
                    )
                    | (
                        ~Q(status=UserStatus.PENDING_DELETION)
                        & Q(deletion_due_at__isnull=True)
                    )
                ),
                name="ck_user_status_deletion_due",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)


class FollowStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"


class Follow(models.Model):
    pk = models.CompositePrimaryKey("follower_id", "followee_id")
    follower = models.ForeignKey(
        User,
        db_column="follower_id",
        on_delete=models.CASCADE,
        related_name="following_relationships",
    )
    followee = models.ForeignKey(
        User,
        db_column="followee_id",
        on_delete=models.CASCADE,
        related_name="follower_relationships",
    )
    status = models.CharField(max_length=10, choices=FollowStatus.choices)
    created_at = models.DateTimeField()
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "FOLLOW"
        indexes = [
            models.Index(
                fields=("followee", "status"),
                name="ix_follow_followee_status",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(follower=models.F("followee")),
                name="ck_follow_not_self",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=FollowStatus.APPROVED, approved_at__isnull=False)
                    | Q(status=FollowStatus.PENDING, approved_at__isnull=True)
                ),
                name="ck_follow_status_approved_at",
            ),
        ]


RATING_VALUES = tuple(Decimal(value) for value in (
    "0.5",
    "1.0",
    "1.5",
    "2.0",
    "2.5",
    "3.0",
    "3.5",
    "4.0",
    "4.5",
    "5.0",
))
VISIBLE_EVENT_STATUSES = ("active", "unverified")


class DiaryEntryQuerySet(models.QuerySet):
    def visible_to(self, viewer):
        visible = self.filter(event__status__in=VISIBLE_EVENT_STATUSES)
        if viewer is None or not viewer.is_authenticated:
            return visible.filter(user__is_private=False)
        approved = Follow.objects.filter(
            follower=viewer,
            followee_id=models.OuterRef("user_id"),
            status=FollowStatus.APPROVED,
        )
        return visible.annotate(_viewer_follows=models.Exists(approved)).filter(
            Q(user__is_private=False) | Q(user=viewer) | Q(_viewer_follows=True)
        )

    def for_circle(self, viewer):
        followees = Follow.objects.filter(
            follower=viewer,
            status=FollowStatus.APPROVED,
        ).values("followee_id")
        return self.filter(
            event__status__in=VISIBLE_EVENT_STATUSES,
            rating__isnull=False,
            user_id__in=followees,
        )

    def for_circle_average(self, viewer):
        followees = Follow.objects.filter(
            follower=viewer,
            status=FollowStatus.APPROVED,
        ).values("followee_id")
        return self.filter(
            event__status__in=VISIBLE_EVENT_STATUSES,
            rating__isnull=False,
        ).filter(Q(user=viewer) | Q(user_id__in=followees))

    def for_aggregation(self):
        return self.filter(
            event__status__in=VISIBLE_EVENT_STATUSES,
            rating__isnull=False,
        )


class DiaryEntry(models.Model):
    user = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="diary_entries",
    )
    event = models.ForeignKey(
        "catalog.Event",
        db_column="event_id",
        on_delete=models.RESTRICT,
        related_name="diary_entries",
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
    )
    rated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DiaryEntryQuerySet.as_manager()

    class Meta:
        db_table = "DIARY_ENTRY"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "event"),
                name="uq_diary_user_event",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(rating__isnull=True, rated_at__isnull=True)
                    | models.Q(rating__isnull=False, rated_at__isnull=False)
                ),
                name="ck_diary_rating_rated_at",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(rating__isnull=True)
                    | models.Q(rating__in=RATING_VALUES)
                ),
                name="ck_diary_rating_half_star",
            ),
        ]


class ReviewQuerySet(models.QuerySet):
    def visible_to(self, viewer):
        visible = self.filter(
            entry__event__status__in=VISIBLE_EVENT_STATUSES,
        )
        if viewer is None or not viewer.is_authenticated:
            return visible.filter(entry__user__is_private=False)
        approved = Follow.objects.filter(
            follower=viewer,
            followee_id=models.OuterRef("entry__user_id"),
            status=FollowStatus.APPROVED,
        )
        return visible.annotate(_viewer_follows=models.Exists(approved)).filter(
            Q(entry__user=viewer)
            | Q(entry__user__is_private=False)
            | Q(_viewer_follows=True)
        )

    def for_public_section(self):
        return self.filter(
            entry__event__status__in=VISIBLE_EVENT_STATUSES,
            entry__user__is_private=False,
        )


class Review(models.Model):
    entry = models.OneToOneField(
        DiaryEntry,
        db_column="entry_id",
        on_delete=models.CASCADE,
        related_name="review",
    )
    body = models.CharField(max_length=1000)
    published_at = models.DateTimeField()

    objects = ReviewQuerySet.as_manager()

    class Meta:
        db_table = "REVIEW"
        constraints = [
            models.CheckConstraint(
                condition=~Q(body__regex=r"^ *$"),
                name="ck_review_body_nonblank",
            ),
        ]


class ReviewLike(models.Model):
    pk = models.CompositePrimaryKey("user_id", "review_id")
    user = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="review_likes",
    )
    review = models.ForeignKey(
        Review,
        db_column="review_id",
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "REVIEW_LIKE"


def active_wbt_event_predicate(at):
    from catalog.models import City

    predicate = Q(pk__in=[])
    for city_id, timezone_name in City.objects.values_list("id", "timezone"):
        local_today = at.astimezone(ZoneInfo(timezone_name)).date()
        predicate |= Q(event__venue__city_id=city_id, event__event_date__gte=local_today)
    return predicate


class WillBeThereQuerySet(models.QuerySet):
    def active_at(self, at, *, event_predicate=None):
        predicate = event_predicate or active_wbt_event_predicate(at)
        return self.filter(
            predicate,
            event__status__in=VISIBLE_EVENT_STATUSES,
        )

    def visible_to(self, viewer, at, *, event_predicate=None):
        visible = self.active_at(at, event_predicate=event_predicate)
        if viewer is None or not viewer.is_authenticated:
            return visible.filter(user__is_private=False)
        approved = Follow.objects.filter(
            follower=viewer,
            followee_id=models.OuterRef("user_id"),
            status=FollowStatus.APPROVED,
        )
        return visible.annotate(_viewer_follows=models.Exists(approved)).filter(
            Q(user__is_private=False) | Q(user=viewer) | Q(_viewer_follows=True)
        )

    def for_public_section(self, at):
        return self.active_at(at).filter(user__is_private=False)

    def for_circle(self, viewer, at):
        followees = Follow.objects.filter(
            follower=viewer,
            status=FollowStatus.APPROVED,
        ).values("followee_id")
        return self.active_at(at).filter(user_id__in=followees).exclude(user=viewer)


class WillBeThere(models.Model):
    pk = models.CompositePrimaryKey("user_id", "event_id")
    user = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="will_be_there_entries",
    )
    event = models.ForeignKey(
        "catalog.Event",
        db_column="event_id",
        on_delete=models.RESTRICT,
        related_name="will_be_there_entries",
    )
    created_at = models.DateTimeField()

    objects = WillBeThereQuerySet.as_manager()

    class Meta:
        db_table = "WILL_BE_THERE"


class NotificationType(models.TextChoices):
    REVIEW_LIKE = "review_like", "Review like"
    FOLLOW = "follow", "Follow"
    FOLLOW_REQUEST = "follow_request", "Follow request"
    REQUEST_ACCEPTED = "request_accepted", "Request accepted"


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        db_column="recipient_id",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        User,
        db_column="actor_id",
        on_delete=models.CASCADE,
        related_name="notification_actions",
    )
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    review = models.ForeignKey(
        Review,
        db_column="review_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_at = models.DateTimeField()
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "NOTIFICATION"
        indexes = [
            models.Index(
                fields=("recipient", "created_at"),
                name="ix_notif_recipient_created",
            ),
            models.Index(
                fields=("recipient", "read_at"),
                name="ix_notification_recipient_read",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(recipient=models.F("actor")),
                name="ck_notification_actor_recipient",
            ),
            models.CheckConstraint(
                condition=(
                    Q(type=NotificationType.REVIEW_LIKE, review__isnull=False)
                    | (
                        ~Q(type=NotificationType.REVIEW_LIKE)
                        & Q(review__isnull=True)
                    )
                ),
                name="ck_notification_type_review",
            ),
        ]
