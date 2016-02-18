from setuptools import setup, find_packages

setup(
    name="parthial",
    version="0.2",
    packages=find_packages(),
    install_requires=["pyyaml"],

    author="benzrf",
    author_email="benzrf@benzrf.com",
    description="Lisp interpreter for user-scriptable "
                "server-side applications",
    long_description=open("README.rst").read(),
    url="https://github.com/benzrf/parthial",
    license='GPLv3',
    zip_safe=True,
    platforms='any',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Lisp',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Interpreters',
    ],
)

