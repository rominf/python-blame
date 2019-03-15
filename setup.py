# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['python_blame']

package_data = \
{'': ['*']}

install_requires = \
['astroid>=2.2,<3.0',
 'docopt>=0.6.2,<0.7.0',
 'plumbum>=1.6,<2.0',
 'poetry-version>=0.1.3,<0.2.0',
 'ruamel.yaml>=0.15.89,<0.16.0']

entry_points = \
{'console_scripts': ['python-blame = python_blame:main']}

setup_kwargs = {
    'name': 'python-blame',
    'version': '0.1.2',
    'description': 'A Python tool and a library for blaming Python code',
    'long_description': None,
    'author': 'Roman Inflianskas',
    'author_email': 'infroma@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
