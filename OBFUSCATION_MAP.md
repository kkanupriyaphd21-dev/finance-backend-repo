# Project Obfuscation Map
Generated: 2026-05-05

## Folder Renames
- `core` → `m01`
- `loans` → `m02` 
- `micro_admin` → `m03`
- `savings` → `m04`
- `microfinance` → `config`
- `templates` → `tpl`
- `static` → `ast`
- `docs` → `doc`
- `java-backend` / `backend-core` → `b01`
- `micro-finance` (backup) → `archive01`
- `realistic-micro-finance` (backup) → `archive02`

## File Renames (Python/Django)
- `apps.py` → `a.py`
- `models.py` → `m.py`
- `views.py` → `v.py`
- `urls.py` → `u.py`
- `forms.py` → `f.py`
- `tests.py` → `t.py`
- `tasks.py` → `tk.py`
- `admin.py` → `ad.py`
- `utils.py` → `ut.py`
- `mixins.py` → `mx.py`
- `settings.py` → `s.py`
- `settings_local.py` → `s_l.py`
- `settings_server.py` → `s_sv.py`
- `wsgi.py` → `w.py`
- `manage.py` → `mg.py`
- `manage_local.py` → `mg_l.py`
- `manage_server.py` → `mg_sv.py`

## File Renames (Root/Config)
- `Procfile` → `pf`
- `README.rst` → `R.rst`
- `app.json` → `a.json`

## Template Renames
All HTML files renamed to: `p001.html` through `p012.html`

## Static Asset Renames
- CSS files: `a01.css` and similar
- JS files renamed with `j` prefix

## Java Backend Renames
- All classes renamed: `C001.java`, `C002.java`, etc.
- Package: `com.example.core` → `x.y.z`
- Package: `dev.kkanupriyaphd.finance` → `x.y.z`

## Migration Renames
Migration files: `0001_initial.py` → `m0001.py`, etc.

## Template Tag Renames
- `recurse.py` → `tg_re.py`
- `loans_tags.py` → `tg_lo.py`
- `ledgertemplatetags.py` → `tg_le.py`

## All Imports Updated
- `from core` → `from m01`
- `from loans` → `from m02`
- `from micro_admin` → `from m03`
- `from savings` → `from m04`
- `from microfinance` → `from config`
- Settings references updated in all files
