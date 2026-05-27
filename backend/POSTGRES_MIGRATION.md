# PostgreSQL migration

The backend uses PostgreSQL when either `DATABASE_URL` or `POSTGRES_DB` is set in `backend/.env`.
Set `FORCE_SQLITE=1` only when you intentionally want to use `backend/db.sqlite3`.

## 1. Create the PostgreSQL database

Create a database that matches `POSTGRES_DB` in `backend/.env`.
For example:

```powershell
createdb -U postgres rdc_ncr_db
```

If your database name contains dashes or uppercase letters, quote it when creating it.

## 2. Export existing SQLite data

Run this while `backend/db.sqlite3` still exists:

```powershell
cd backend
$env:FORCE_SQLITE="1"
$env:PYTHONUTF8="1"
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 -o sqlite_export.json
Remove-Item Env:\FORCE_SQLITE
Remove-Item Env:\PYTHONUTF8
```

## 3. Build the PostgreSQL schema

Make sure `backend/.env` has PostgreSQL settings and does not set `FORCE_SQLITE=1`.

```powershell
python manage.py migrate
```

## 4. Import the SQLite data into PostgreSQL

```powershell
python manage.py loaddata sqlite_export.json
```

## 5. Verify

```powershell
python manage.py check
python manage.py shell -c "from projects.models import Project, User; print('users=', User.objects.count(), 'projects=', Project.objects.count())"
```
