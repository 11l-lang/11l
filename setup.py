import setuptools

setuptools.setup(
    name = '11l',
    py_modules = ['11l', 'python_to_11l/tokenizer', 'python_to_11l/parse', '_11l_to_cpp/tokenizer', '_11l_to_cpp/parse'],
    version = '0.1.1',
    description = 'A Python implementation of transpilers Python → 11l and 11l → C++',
#    long_description = open('README.md', encoding = 'utf-8').read(),
#    long_description_content_type = 'text/markdown',
    author = 'Alexander Tretyak',
    author_email = 'alextretyak@users.noreply.github.com',
    url = 'http://11l-lang.org',
    license = 'MIT',
    install_requires = ['thindf'],
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
