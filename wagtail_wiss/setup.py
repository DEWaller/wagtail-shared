from setuptools import setup, find_packages

setup(
    name='wagtail-wiss',
    version='0.1.0',
    description='WiSS Wagtail extensions: maps, events, and more',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David Waller',
    author_email='david@wiss.co.uk',
    url='https://github.com/DEWaller/wagtail-wiss',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'wagtail>=5.2',
        'Django>=4.2',
    ],
    classifiers=[
        'Framework :: Wagtail',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
