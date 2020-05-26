import os

from setuptools import find_packages, setup


# Dynamically calculate the version
version = __import__('djimporter').get_version()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="djimporter",
    version=version,
    url='https://github.com/ico-apps/django-importer',
    author='ICO - Institut Catala Ornitologia',
    author_email='ico@ornitologia.org',
    description='Ornithology oriented monitoring data management tool',
    long_description=('Django importer, another CSV import library.'),
    # TODO license = 'XXX License',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django==2.2.10", "django-background-tasks==1.2.5"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
