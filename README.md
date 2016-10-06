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
SELECTEL_BACKUP_CONTAINER = 'backup'
SELECTEL_STATIC_CONTAINER = 'mystatic'

# serve from cloud
SELECTEL_STATIC_CONTAINER_URL = 'http://xxxxx.selcdn.ru/{}/'.format(SELECTEL_STATIC_CONTAINER)

# OR from http CDN
SELECTEL_STATIC_CONTAINER_URL = 'http://xxxxx.selcdn.com/{}/'.format(SELECTEL_STATIC_CONTAINER)

# OR from https CDN
SELECTEL_STATIC_CONTAINER_URL = 'https://customdomain-a.akamaihd.net/

STATIC_URL = SELECTEL_STATIC_CONTAINER_URL
STATICFILES_STORAGE = 'django_selectel.storage.StaticSelectelStorage'

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
