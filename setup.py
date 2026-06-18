import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Package dependencies
install_requires = [
    'django>=3.0',
]

# Testing dependencies
testing_extras = [
]

# Documentation dependencies
documentation_extras = [
]

release_extras = [
    'build>=1.0',
    'twine>=5.0',
]

setup(
    name='django-askell',
    version='0.1.25',
    packages=find_packages(exclude=['test_project', 'test_project.*']),
    include_package_data=True,
    license='MIT',
    description='Recurring payments solution Askell integration for Django and Wagtail (optional)',
    long_description=README,
    url='https://github.com/overcastsoftware/django-askell/',
    author='Overcast',
    author_email='hallo@overcast.is',
    long_description_content_type="text/markdown",
    python_requires='>=3.9',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 3',
        'Framework :: Wagtail :: 4',
        'Framework :: Wagtail :: 5',
        'Framework :: Wagtail :: 6',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        'docs': documentation_extras,
        'release': release_extras,
    },
)
