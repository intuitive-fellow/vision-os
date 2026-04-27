# AGENT.md

This file provides guidance to AI agents when working with code in this repository.

## Project

VisionOS backend — a Django REST Framework API that helps users turn a life vision into daily actions (Vision → Activities → Tasks → Daily Execution → Progress).

## Commands

All commands use `uv run` (the project is managed with [uv](https://github.com/astral-sh/uv)).

```bash
uv run python manage.py runserver          # start dev server
uv run python manage.py migrate            # apply migrations
uv run python manage.py makemigrations     # generate migrations
uv run python manage.py createsuperuser    # create admin user
uv run python manage.py test               # run all tests
uv run python manage.py test apps.areas    # run a single app's tests
```

## Architecture

### Settings layout

Settings are split across two directories:

- `config/django/` — environment tiers: `base.py`, `local.py`, `production.py`
- `config/settings/` — feature slices imported at the bottom of `base.py`: `jwt.py`, `email.py`
- `config/env.py` — loads `django-environ`; all env vars are read through `env()`
- `.env` — required env vars (see existing file for all keys)

### App layout

All Django apps live under `apps/`. Each app follows this structure:

```
apps/<name>/
    models.py
    admin.py
    choices.py          # TextChoices enums
    schemas/<purpose>.py  # Pydantic input schemas (validation)
    services/<name>.py  # business logic layer
    api/v1.py           # view classes for v1
    urls/u1.py          # URL patterns for v1
```

URL files are named `u1.py`, `u2.py` per version. View files are named `v1.py`, `v2.py` per version.

### `apps/base/` — shared primitives

Every new app should build on these:

| File | What it provides |
|---|---|
| `models.py` | `BaseModel` — abstract with `created_at`, `updated_at`, `deleted_at` |
| `views.py` | `BaseAPIView` (JWT auth, `IsAuthenticated`) and `UnauthenticatedAPIView` (public) |
| `exceptions.py` | `AppException` hierarchy + global `custom_exception_handler` |
| `schemas.py` | `BaseInputSchema` — Pydantic base for all input schemas |
| `constants.py` | `OPTIONAL`, `CASCADE`, `SET_NULL` dicts for model field kwargs |

### Response & error conventions

Views must use `self.success()`, `self.created()`, or `self.no_content()` — never construct a raw `Response` for success cases.

Raise exceptions from `apps.base.exceptions` instead of returning error responses:

```python
from apps.base.exceptions import ValidationException, NotFoundException, PermissionException

raise ValidationException("Some message")
raise NotFoundException()
```

All API responses follow this envelope:

```json
{ "success": true,  "message": "...", "data": { ... } }
{ "success": false, "message": "...", "errors": { ... } | null }
```

### Authentication

Email-OTP flow: `POST /api/v1/auth/send-otp/` → `POST /api/v1/auth/verify-otp/` → JWT pair returned. Subsequent requests use `Authorization: Bearer <access_token>`. Refresh via `POST /api/v1/auth/refresh/`, logout via `POST /api/v1/auth/logout/` (blacklists the refresh token).

`User` model uses email as `USERNAME_FIELD`; `username` is auto-generated and not exposed to users.

### Service layer

Business logic lives exclusively in service classes under `services/`. Views instantiate or call service methods directly — models and views contain no business logic.

```python
class AreaCRUDService:
    @classmethod
    def get_area_list(cls, user) -> list[dict]: ...

    @classmethod
    def create_area(cls, user, validated_data: dict) -> dict: ...
```

### Model conventions

- All models extend `BaseModel` (soft-delete via `deleted_at`).
- Use `OPTIONAL`, `CASCADE`, `SET_NULL` from `apps.base.constants` for repetitive field kwargs.
- Soft-deleted records are excluded by filtering `deleted_at__isnull=True` in service querysets.