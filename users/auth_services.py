import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.core.signing import salted_hmac
from django.db import transaction
from django.utils.timezone import now as timezone_now

from .models import AccountCode, AccountCodePurpose, User


CODE_LIFETIME = timedelta(minutes=15)
CODE_COOLDOWN = timedelta(seconds=60)
CODE_ATTEMPT_LIMIT = 5
VERIFICATION_REQUIRED_MESSAGE = (
    "Email verification is required for account actions."
)


class AccountActionVerificationRequired(Exception):
    pass


class CodeCooldown(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__("A new code cannot be sent yet.")


class CodeInvalid(Exception):
    pass


class CodeExpired(CodeInvalid):
    pass


class CodeAttemptLimit(CodeInvalid):
    pass


def account_actions_allowed(user):
    return (
        not settings.EMAIL_VERIFICATION_ENFORCED
        or user.email_verified_at is not None
    )


def require_account_action(user):
    if not account_actions_allowed(user):
        raise AccountActionVerificationRequired(VERIFICATION_REQUIRED_MESSAGE)


def require_account_action_for_user_id(user_id):
    if not settings.EMAIL_VERIFICATION_ENFORCED:
        return
    user = User.objects.only("email_verified_at").get(pk=user_id)
    require_account_action(user)


def _code_hash(user_id, purpose, code):
    return salted_hmac(
        "danced.account-code",
        f"{user_id}:{purpose}:{code}",
        algorithm="sha256",
    ).hexdigest()


def _email_copy(purpose, code):
    if purpose == AccountCodePurpose.EMAIL_VERIFICATION:
        return (
            "Your Danced verification code",
            f"Your Danced email verification code is {code}. It expires in 15 minutes.",
        )
    return (
        "Your Danced password reset code",
        f"Your Danced password reset code is {code}. It expires in 15 minutes.",
    )


@transaction.atomic
def issue_account_code(*, user, purpose):
    user = User.objects.select_for_update().get(pk=user.pk)
    now = timezone_now()
    record = (
        AccountCode.objects.select_for_update()
        .filter(user=user, purpose=purpose)
        .first()
    )
    if record is not None and now < record.sent_at + CODE_COOLDOWN:
        remaining = int((record.sent_at + CODE_COOLDOWN - now).total_seconds())
        raise CodeCooldown(max(1, remaining))

    code = f"{secrets.randbelow(1_000_000):06d}"
    values = {
        "code_hash": _code_hash(user.pk, purpose, code),
        "sent_at": now,
        "expires_at": now + CODE_LIFETIME,
        "failed_attempts": 0,
        "consumed_at": None,
    }
    if record is None:
        AccountCode.objects.create(user=user, purpose=purpose, **values)
    else:
        for field, value in values.items():
            setattr(record, field, value)
        record.save(update_fields=tuple(values))

    subject, body = _email_copy(purpose, code)
    send_mail(subject, body, None, (user.email,))
    return code


def _consume_account_code_locked(*, user, purpose, code):
    now = timezone_now()
    record = (
        AccountCode.objects.select_for_update()
        .filter(user=user, purpose=purpose)
        .first()
    )
    if record is None or record.consumed_at is not None:
        return now, CodeInvalid("The code is invalid.")
    if record.failed_attempts >= CODE_ATTEMPT_LIMIT:
        return now, CodeAttemptLimit(
            "Too many incorrect attempts. Request a new code."
        )
    if now >= record.expires_at:
        return now, CodeExpired("The code has expired. Request a new code.")
    if not secrets.compare_digest(
        record.code_hash,
        _code_hash(user.pk, purpose, code),
    ):
        record.failed_attempts += 1
        record.save(update_fields=("failed_attempts",))
        error = (
            CodeAttemptLimit("Too many incorrect attempts. Request a new code.")
            if record.failed_attempts >= CODE_ATTEMPT_LIMIT
            else CodeInvalid("The code is invalid.")
        )
        return now, error
    record.consumed_at = now
    record.save(update_fields=("consumed_at",))
    return now, None


def consume_account_code(*, user, purpose, code):
    with transaction.atomic():
        now, error = _consume_account_code_locked(
            user=user,
            purpose=purpose,
            code=code,
        )
    if error is not None:
        raise error
    return now


def verify_email(*, user, code):
    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)
        verified_at, error = _consume_account_code_locked(
            user=locked_user,
            purpose=AccountCodePurpose.EMAIL_VERIFICATION,
            code=code,
        )
        if error is None and locked_user.email_verified_at is None:
            locked_user.email_verified_at = verified_at
            locked_user.save(update_fields=("email_verified_at",))
    if error is not None:
        raise error
    return verified_at


def request_password_reset(*, email):
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        return
    try:
        issue_account_code(user=user, purpose=AccountCodePurpose.PASSWORD_RESET)
    except CodeCooldown:
        # The public response is deliberately identical for missing accounts and
        # throttled existing accounts.
        pass


def _delete_user_sessions(user_id):
    session_keys = []
    for session in Session.objects.filter(expire_date__gte=timezone_now()):
        if session.get_decoded().get("_auth_user_id") == str(user_id):
            session_keys.append(session.session_key)
    if session_keys:
        Session.objects.filter(session_key__in=session_keys).delete()


def reset_password(*, user, code, password):
    password_validation.validate_password(password, user=user)
    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)
        _reset_at, error = _consume_account_code_locked(
            user=locked_user,
            purpose=AccountCodePurpose.PASSWORD_RESET,
            code=code,
        )
        if error is None:
            locked_user.set_password(password)
            locked_user.save(update_fields=("password",))
            _delete_user_sessions(locked_user.pk)
    if error is not None:
        raise error
