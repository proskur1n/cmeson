from setuptools import setup
import sys

long_description = open('README.md').read()

data_files = []
if sys.platform != 'win32':
	data_files.append(('share/man/man1', ['docs/cmeson.1']))

setup(
	name = 'cmeson',
	author = 'Andrey Proskurin (proskur1n)',
	author_email = 'andreyproskurin@protonmail.com',
	license = 'MIT',
	description = 'TUI for meson build system',
	long_description_content_type = 'text/markdown',
	long_description = long_description,
	url = 'https://github.com/proskur1n/cmeson',
	version = '1.0.0',
	download_url = 'https://github.com/proskur1n/cmeson/archive/refs/tags/1.0.0.tar.gz',
	packages = ['cmeson'],
	install_requires = ['urwid', 'meson>=0.5'],
	entry_points = {
		'console_scripts': ['cmeson=cmeson.__main__:main']
	},
	keywords = 'cmeson meson build system TUI',
	data_files = data_files,
)