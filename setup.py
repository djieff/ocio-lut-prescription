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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
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
            'ocio-lut-prescription=ocio_lut_prescription.__main__:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='ocio-lut-prescription',
    name='ocio-lut-prescription',
    packages=find_packages(include=['ocio_lut_prescription', 'ocio_lut_prescription.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/djieff/ocio-lut-prescription',
    version='1.1.0',
    zip_safe=False,
)
