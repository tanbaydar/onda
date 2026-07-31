from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q


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
