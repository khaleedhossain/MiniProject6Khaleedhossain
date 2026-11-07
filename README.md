# Recipe Box — Mini Project 6 (Django)

**INF601 – Advanced Programming in Python**
Khaleed Hossain

A Django rebuild of the Recipe Box app from Mini Project 5 (which was built
in Flask): users register and log in, then add their own recipes — a
title, an ingredient list, and instructions — and can edit or delete only
the recipes they authored. Anyone, logged in or not, can browse and read
recipes.

## Project layout

```
MiniProject6Khaleedhossain/
├── requirements.txt
└── mysite/                   # django-admin startproject mysite
    ├── manage.py
    ├── mysite/                # project config
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── recipes/               # the app (python manage.py startapp recipes)
        ├── models.py          # Recipe, Ingredient
        ├── admin.py           # styled admin: inline ingredients, list_display, search, filters
        ├── forms.py           # RecipeForm, RegisterForm, LoginForm (Bootstrap classes on widgets)
        ├── views.py           # index, detail, create, update, delete, register
        ├── middleware.py      # AdminIPAllowlistMiddleware (Week 12 security fix)
        ├── urls.py
        └── templates/
            ├── base.html                 # Bootstrap 5 navbar/layout
            ├── recipes/
            │   ├── index.html            # card grid of all recipes
            │   ├── my_recipes.html       # current user's own recipes
            │   ├── detail.html           # ingredients + instructions + delete modal
            │   └── recipe_form.html      # shared create/update form
            └── registration/
                ├── login.html
                └── register.html
```

## Database

SQLite (Django's default), two models linked by a foreign key:

| Model | Fields | Linked by |
|---|---|---|
| `Recipe` | title, instructions, created, author | `author` → Django's built-in `User` |
| `Ingredient` | description, position, recipe | `recipe` → `Recipe` |

A recipe's ingredients are entered as one per line in a textarea; the view
splits them into separate `Ingredient` rows linked back to the recipe by
`recipe_id`, rather than storing them as one text blob.

## Install

```bash
cd MiniProject6Khaleedhossain
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # if that fails on your Python version, `pip install django` instead
cd mysite
```

## Initialize the database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # for /admin/ access
```

## Run the development server

**Locally:**
```bash
python manage.py runserver
```
Open <http://127.0.0.1:8000>.

**On the course dev box** (per the Mini Project 6 instructions — bind to
all interfaces so the lab's reverse proxy can reach it, and set your dev
box's site hostname so Django accepts the request and trusts it for CSRF).
As of the Week 12 security fixes below, also set `DJANGO_SECRET_KEY` (every
deployment needs its own, never committed):

```bash
export DJANGO_ALLOWED_HOST=YOUR_SITE_HOSTNAME   # no https://, from the private Dev Box Access feedback
export DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
python manage.py runserver 0.0.0.0:8000
```

`settings.py` reads `DJANGO_ALLOWED_HOST` and adds it to both
`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (with `https://` prepended for
the latter) — see the top of `mysite/settings.py`. Run this inside `tmux`
so the server survives closing the browser tab.

## Security fixes (Week 12)

Three findings were filed against this site during the Week 12 pentest
exercise and fixed. Each entry is root cause → fix → where.

1. **`DEBUG = True` leaked tracebacks/settings on any bad URL.**
   Root cause: the tutorial default (`DEBUG = True`) was never turned off
   for the dev-box deployment. Fix: `DEBUG` now reads from `DJANGO_DEBUG`
   and **defaults to `False`** — secure by default, opt into debug mode
   locally only. See `mysite/settings.py`.

2. **`SECRET_KEY` was a literal string committed to the public repo.**
   Root cause: same tutorial-default pattern — `startproject` generates a
   real key directly in `settings.py`. Fix: `SECRET_KEY` now reads from
   `DJANGO_SECRET_KEY` with an obviously-fake placeholder
   (`django-insecure-local-dev-only-placeholder-do-not-deploy-with-this`)
   as the local-only fallback. The old committed key must be treated as
   permanently burned (it's in git history forever) — the dev box needs a
   **freshly generated** key via the env var above, not a different literal
   baked into the file. See `mysite/settings.py`.

3. **`/admin/` was reachable by anyone who found it.**
   Root cause: Django's admin is mounted at the well-known `/admin/` path
   with no additional gate beyond its own login form. Fix: added
   `recipes/middleware.py`'s `AdminIPAllowlistMiddleware` — when
   `DJANGO_ADMIN_ALLOWED_IPS` (comma-separated IPs) is set, `/admin/`
   returns `403` for any other client IP; left unset, behavior is
   unchanged (so this doesn't break grading access by default). It reads
   `X-Forwarded-For` since the dev box sits behind a reverse proxy. This
   is a mitigation, not a complete fix — the real minimum bar per the
   finding is **a strong, unique superuser password**, which has to be set
   by hand on the dev box (see below), since I don't have that password
   and can't rotate it remotely.

### Action required on the dev box (not something code alone fixes)

```bash
# after git pull on the dev box, inside tmux:
export DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
export DJANGO_ALLOWED_HOST=YOUR_SITE_HOSTNAME
# optional, once a specific grading/instructor IP is known:
# export DJANGO_ADMIN_ALLOWED_IPS=1.2.3.4

python manage.py changepassword admin   # rotate to a strong, unique password
python manage.py runserver 0.0.0.0:8000
```

## Pages / routes

| Route | Page | Notes |
|---|---|---|
| `/` | Recipe list | Public. Card grid of every recipe. |
| `/mine/` | My Recipes | Login required. Just the current user's own recipes, with quick Edit links. |
| `/<id>/` | Recipe detail | Public. Ingredients + instructions; delete button (owner only) opens a **Bootstrap modal** to confirm before the destructive POST. |
| `/create/` | New recipe | Login required. `GET` renders the form, `POST` validates and saves it. |
| `/<id>/update/` | Edit recipe | Login + ownership required (403 otherwise). Same form, pre-filled. |
| `/accounts/register/` | Register | Custom view/form (Django has no built-in register view). |
| `/accounts/login/` | Log in | Django's built-in `LoginView`, with a Bootstrap-styled form. |
| `/accounts/logout/` | Log out | Django's built-in `LogoutView` (POST-only as of Django 5+, so it's a button, not a link). |
| `/admin/` | Django admin | `Recipe` admin shows an inline `Ingredient` editor, `list_display`/`list_filter`/`search_fields`, and a computed ingredient count column. |

Bootstrap 5 (via CDN) styles the navbar, forms, cards, alerts, and the
delete-confirmation modal.

## Requirements coverage

- Header comments (name/class/project) on every custom `.py` file.
- One app (`recipes`) inside the `mysite` project, standard Django layout.
- 6 templated pages (index, my-recipes, detail, create/update form, login,
  register), all extending a shared `base.html`.
- Forms: `/create/`, `/<id>/update/`, `/accounts/register/`,
  `/accounts/login/`.
- Django admin: inline `Ingredient` editor on `Recipe`, `list_display`,
  `list_filter`, `search_fields`, `date_hierarchy`, and a computed column.
- Bootstrap 5, including a modal (delete confirmation).
- Register/login system via `django.contrib.auth`.
- 6 commits on `main`, `requirements.txt` included.

## Verified end-to-end

Ran the dev server locally and drove it with `curl` through real
CSRF-protected form submissions (not internal function calls): registered
a user, logged in, created a recipe (confirmed each ingredient line became
its own linked `Ingredient` row), viewed it on the index and detail pages,
logged into `/admin/` and confirmed the inline ingredients and computed
`ingredient_count` column render correctly, registered a second user and
confirmed they get `403` trying to edit the first user's recipe, and
confirmed anonymous visitors can read recipes but are redirected to log in
before creating one.

## AI Usage

Built with Claude Code, continuing directly from the Flask version (Mini
Project 5) of the same app.

**Done by Claude Code:**
- Scaffolded the project with the exact commands from the assignment
  (`django-admin startproject mysite`, `python manage.py startapp
  recipes`), then wrote `models.py`, `admin.py`, `forms.py`, `views.py`,
  `urls.py`, and all templates.
- Translated the Flask version's data model and ownership logic into
  idiomatic Django: `django.contrib.auth`'s `User` model instead of a
  hand-rolled auth table, `ModelForm`/`UserCreationForm`/`AuthenticationForm`
  instead of manually reading `request.form`, and Django's admin site
  (customized with an inline `Ingredient` editor and a computed
  `ingredient_count` column) instead of a hand-built admin page.
- Added the `DJANGO_ALLOWED_HOST` environment-variable pattern in
  `settings.py` so the same code works unmodified on the dev box once that
  variable is set, without hard-coding the dev box's private hostname into
  the repo.
- Ran the full flow against the real dev server with `curl` (register,
  login, create, detail, admin, cross-user 403, anonymous read access) to
  confirm the app actually works, not just that the code looks right.

**Done by me:**
- Supplied the dev box constraints from the course instructions (2FA
  sign-in, `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`, running inside `tmux`)
  that the AI can't act on directly, since those require my own
  credentials and phone.
- Reviewed the authorization logic (ownership checks on update/delete) and
  the admin customization.
- Will run the actual deployment steps on the dev box myself and confirm
  the site loads at the real site address.
