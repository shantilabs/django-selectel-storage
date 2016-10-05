import logging
import subprocess
import tempfile

from django.conf import settings
from django.utils.timezone import now

from .storage import SelectelStorage


logger = logging.getLogger('selectel')


def pg_backup(dbname='default'):
    d = settings.DATABASES[dbname]
    name = '{}{}{}.sql.gz'.format(
        'debug-' if settings.DEBUG else '',
        d['NAME'],
        now().isoformat().split('.')[0].replace(':', ''),
    )
    logger.info('backup: %s', name)
    storage = SelectelStorage(settings.SELECTEL_BACKUP_CONTAINER)
    with tempfile.TemporaryFile() as tf:
        p1 = subprocess.Popen([
            'pg_dump',
            'postgresql://{USER}:{PASSWORD}@{HOST}/{NAME}'.format(**d),
        ], stdout=subprocess.PIPE)
        p2 = subprocess.Popen('gzip', stdin=p1.stdout, stdout=tf)
        p1.stdout.close()
        stdout, stderr = p2.communicate()
        assert not p1.returncode, p1.returncode
        assert not p2.returncode, p2.returncode
        if stderr:
            logger.warn(stderr)
        storage.save(name, tf)
