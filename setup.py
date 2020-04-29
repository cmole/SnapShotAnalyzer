from setuptools import setup

setup(
    name='snapshotalyzer',
    version='0.1',
    author='Christian Mueller',
    author_email='christianmueller.321@gmail.com',
    description='Snapshotalyzer is a tool for manageing EC2 instances and snapshots',
    license='GPLv3+',
    packages=['shotty'],
    url='https://github.com/cmole/SnapShotAnalyzer',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    '''
)