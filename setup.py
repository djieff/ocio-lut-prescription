from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['PySide2']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Jean-Francois Bouchard",
    author_email='bouchard.jfrancois@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre - Alpha'
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
    description="GUI wrapper of ociobakelut command.",
    entry_points={
        'console_scripts': [
            'ocioLutPrescription=ocioLutPrescription.__main__:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='ocioLutPrescription',
    name='ocioLutPrescription',
    packages=find_packages(include=['ocioLutPrescription', 'ocioLutPrescription.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/djieff/ocioLutPrescription',
    version='1.0.0',
    zip_safe=False,
)
