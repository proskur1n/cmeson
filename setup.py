from setuptools import setup

long_description = open('README.md').read()

setup(
	name = 'cmeson',
	author = 'Andrey Proskurin (proskur1n)',
	# TODO email
	license = 'MIT',
	description = 'TUI for meson build system',
	long_description_content_type = 'text/markdown',
	long_description = long_description,
	# TODO url / download_url
	# TODO version ?
	packages = ['cmeson'],
	install_requires = ['urwid', 'meson>=0.5'],
	entry_points = {
		'console_scripts': ['cmeson=cmeson.__main__:main']
	},
	keywords = 'cmeson meson build system TUI',
)