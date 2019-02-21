from setuptools import setup, find_packages
from os.path import join, dirname

import textPreprocessor

setup(
    name='textPreprocessor',
    description='This project makes saving/loading procedure easier for classes with inheritance.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    version=textPreprocessor.__version__,
    url='https://github.com/Valtonis/textPreprocessor.git',
    author='Alexander Gusarin',
    author_email='alex.gusarin@gmail.com',
    license='MIT',
    packages=find_packages(),
	install_requires=['serializableClass', 'spacy', 'pymorphy2']
)