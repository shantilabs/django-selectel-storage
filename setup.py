from distutils.core import setup


setup(
    name='django-selectel-storage',
    version='1.3',
    author='Maxim Oransky',
    author_email='maxim.oransky@gmail.com',
    url='https://github.com/shantilabs/django-selectel-storage',
    packages=[
        'django_selectel',
        'django_selectel.management',
        'django_selectel.management.commands',
    ],
)
