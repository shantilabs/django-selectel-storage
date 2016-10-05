# Based on:
#   - https://support.selectel.ru/storage/api_info/
#   - https://github.com/blacktorn/django-storage-swift
from __future__ import unicode_literals

from datetime import datetime
from io import BytesIO
import logging
import os
import time

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import requests


logger = logging.getLogger('selectel')


@deconstructible
class SelectelStorage(Storage):
    container_name = settings.SELECTEL_STATIC_CONTAINER
    use_cache = getattr(settings, 'SELECTEL_CACHE', False)  # experimental
    auth_url = 'https://auth.selcdn.ru'

    def __init__(self, container_name=None):
        if container_name:
            self.container_name = container_name
        self.sess = requests.Session()
        self._storage_url = None
        self._token = None
        self._files_cache = set()

    @property
    def token(self):
        if not self._token:
            self._lazy_init()
        return self._token

    @property
    def storage_url(self):
        if not self._storage_url:
            self._lazy_init()
        return self._storage_url

    def _lazy_init(self):
        logger.debug('init')
        r = self.sess.get(self.auth_url, headers={
            'X-Auth-User': settings.SELECTEL_USER,
            'X-Auth-Key': settings.SELECTEL_KEY,
        })
        assert r.status_code == 204, r
        self._storage_url = r.headers['x-storage-url'].rstrip('/')
        self._token = r.headers['x-auth-token']

    def _open(self, name, mode='rb'):
        logger.debug('_open(%s): %s', mode, name)
        r = self.sess.get(self.url(name), headers={
            'X-Auth-Token': self.token,
        })
        if r.status_code == 404:
            msg = 'File %r not found at %s' % (name, self.url())
            logger.warn(msg)
            raise IOError(msg)
        assert 200 <= r.status_code < 400, (r.status_code, r.text)
        buf = BytesIO(r.content)
        buf.name = os.path.basename(name)
        buf.mode = mode
        return File(buf)

    def _save(self, name, content):
        logger.debug('_save: %s', name)
        r = self.sess.put(self.url(name), data=content, headers={
            'X-Auth-Token': self.token,
        })
        assert r.status_code == 201
        if self.use_cache:
            self._files_cache.add(name)
        return name

    def _get_headers(self, name):
        r = self.sess.head(self.url(name), headers={
            'X-Auth-Token': self.token,
        })
        return None if r.status_code == 404 else r.headers

    def exists(self, name):
        if not self.use_cache:
            result = bool(self._get_headers(name))
        elif name in self._files_cache:
            result = True
        else:
            result = bool(self._get_headers(name))
            if result:
                self._files_cache.add(name)
        logger.debug('exists: %s = %r', name, result)
        return result

    def size(self, name):
        logger.debug('size: %s', name)
        return int(self._get_headers(name)['content-length'])

    def modified_time(self, name):
        logger.debug('modified_time: %s', name)
        return datetime.fromtimestamp(float(self._get_headers(name)['x-timestamp']))  # noqa

    def url(self, name=''):
        name = name.lstrip('/')
        return '{}/{}/{}'.format(self.storage_url, self.container_name, name)

    def copy(self, src, dst):
        r = self.sess.put(self.url(dst), headers={
            'X-Auth-Token': self.token,
            'X-Copy-From': '/{}/{}'.format(self.container_name, src.lstrip('/'))
        })
        assert r.status_code == 201, (r.status_code, r.content)

    def listdir(self, path='/'):
        logger.debug('listdir: %s', path)
        files = []
        dirs = []
        path = path.lstrip('/')
        assert not path or path.endswith('/')
        for d in self._listdir(path):
            bits = d['name'][len(path):].split('/')
            name = bits[0]
            if len(bits) == 1:
                files.append(name)
            elif name not in dirs:
                dirs.append(name)
        return dirs, files

    def _listdir(self, path='', limit=500):
        logger.debug('_listdir: %r', path)
        marker = ''
        while True:
            found = False
            for d in self.sess.get(self.url(), params={
                'path': path,
                'format': 'json',
                'marker': marker,
                'limit': limit,
            }, headers={
                'X-Auth-Token': self.token,
            }).json():
                yield d
                marker = d['name']
                found = True
            if not found:
                break

    def delete(self, name):
        logger.debug('delete: %s', name)
        for attempt in range(10):
            r = self.sess.delete(self.url(name), headers={
                'X-Auth-Token': self.token,
            })
            if r.status_code == 503:
                logger.warn(r.content)
                time.sleep(attempt + 1)
                continue
            break
        if r.status_code == 404:
            pass
        else:
            assert r.status_code == 204, (r.status_code, r.content)
        if self.use_cache and name in self._files_cache:
            self._files_cache.remove(name)


class StaticSelectelStorage(SelectelStorage):
    def get_available_name(self, name, max_length=None):
        return name
