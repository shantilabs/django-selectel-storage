# django-selectel-storage

## settings.py

```
INSTALLED_APPS = (
    # ...
    'django_selectel',
)

# creds from https://support.selectel.ru/storage/users/
SELECTEL_USER = '12345'
SELECTEL_KEY = '*****'

# you should create this containers and allow access
SELECTEL_STATIC_CONTAINER = 'mystatic'
SELECTEL_BACKUP_CONTAINER = 'backup'

# static
STATICFILES_STORAGE = 'django_selectel.storage.StaticSelectelStorage'
STATIC_URL = 'https://xxxxx.selcdn.ru/{}/'.format(SELECTEL_STATIC_CONTAINER)

# django-compressor
COMPRESS_STORAGE = STATICFILES_STORAGE
COMPRESS_URL = STATIC_URL

# django-imagekit
IMAGEKIT_DEFAULT_FILE_STORAGE = 'django_selectel.storage.SelectelStorage'

```


## Backups from Celery (Postgres only)

```
from django_selectel.backups import pg_backup

@app.task()
def my_backup():
    pg_backup()
    
```

## Backups from CLI (Postgres only)

```
manage.py pg_backup
```
