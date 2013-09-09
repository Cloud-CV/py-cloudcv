from setuptools import setup

setup(
    name='PCloudCV',
    version='0.0.1',
    author='Harsh Agrawal, Dr. Dhruv Batra',
    author_email='h.agrawal092@gmail.com, dbatra@vt.edu',
    packages=['pcloudcv'],
    url='http://github.com/batra-mlp-lab/pcloudcv',
    license='LICENSE.txt',
    description='CloudCV Python APIs',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 1.2.3",
        "redis >= 2.7.6",
        "colorama >= 0.2.5",
        "poster >= 0.8.1",
        "socketIO-client >= 0.4",
    ],
)
