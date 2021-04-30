import urwid
import subprocess
import json
import getopt
import sys
import os
from .command import LayoutCommandOutput
from .optionlist import LayoutOptionList
from .screen import Screen

usage = """\
cmeson [OPTIONS] builddir [sourcedir] [TRAILING]

cmeson is a TUI for the meson build system

  -h, --help           Show this message and exit
  --backend BACKEND    Select backend to query build options for. See meson
                       documentation for possible BACKEND values

TRAILING options are passed as-is to 'meson setup' or 'meson configure'"""

def pop_non_argument(trailing):
	if trailing[0].startswith('-'):
		raise IndexError
	return trailing.pop(0)

"""
A hacky way to find out if we should run 'meson setup' or 'meson configure'
when configuring the project
"""
def is_configured_project(builddir):
	cmd = ['meson', 'introspect', '--projectinfo', builddir]
	return subprocess.call(
		cmd,
		stderr=subprocess.DEVNULL,
		stdout=subprocess.DEVNULL) == 0

"""
dargument = -D argument

Returns list of darguments ['-Da=b', '-Dc=d', ...] for build options that
have changed and need to be reconfigured
"""
def get_darguments(option_list):
	widgets = map(lambda x: x[0], option_list.build_options())
	changed = filter(lambda x: x.changed(), widgets)
	dargs = []
	for widget in changed:
		darg = '-D{}={}'.format(widget.name, widget.get_value())
		dargs.append(darg)
	return dargs

class ApplicationError(Exception):
	pass

class Application:
	palette = [
		('selected', 'bold,standout', ''),
		('description', 'bold,standout', '')
	]

	def __init__(self, argv):
		self.parse_arguments(argv)
		self.configured = is_configured_project(self.builddir)

		layout = LayoutOptionList(self.get_build_options())
		urwid.connect_signal(layout, 'configure', self.configure_meson)
		self.layout_option_list = layout

		urwid.set_encoding('utf-8')
		self.main_loop = urwid.MainLoop(
			layout,
			palette=self.palette,
			screen=Screen(),
			handle_mouse=False)
		self.main_loop.run()
	
	def parse_arguments(self, argv):
		try:
			optlist, trailing = getopt.getopt(argv[1:], 'h', ['help', 'backend='])
		except getopt.GetoptError as e:
			raise ApplicationError(e)
		
		self.trailing = trailing
		self.backend = None
		self.sourcedir = '.'

		for opt, arg in optlist:
			if opt in ('-h', '--help'):
				print(usage)
				sys.exit()
			if opt == '--backend':
				self.backend = arg
			else:
				assert False, 'unhandled option'

		try:
			self.builddir = pop_non_argument(self.trailing)
		except IndexError:
			raise ApplicationError('builddir not specified')
		
		try:
			self.sourcedir = pop_non_argument(self.trailing)
		except IndexError:
			pass
		else:
			self.get_meson_build_path()
		
		try:
			if os.path.samefile(self.builddir, self.sourcedir):
				raise ApplicationError('builddir equals sourcedir')
		except FileNotFoundError:
			pass
	
	def get_meson_build_path(self):
		path = os.path.join(self.sourcedir, 'meson.build')
		if not os.path.isfile(path):
			raise ApplicationError('sourcedir not valid')
		return path

	def get_build_options(self):
		cmd = ['meson', 'introspect', '--buildoptions']
		if self.backend:
			cmd.extend(['--backend', self.backend])
		if self.configured:
			cmd.append(self.builddir)
		else:
			cmd.append(self.get_meson_build_path())

		try:
			json_str = subprocess.check_output(
				cmd,
				stderr=subprocess.PIPE,
				text=True)
		except subprocess.CalledProcessError as e:
			msg = 'could not get build options'
			if e.stderr:
				msg += ':\n\n' + e.stderr
			raise ApplicationError(msg)

		return json.loads(json_str)
	
	def configure_meson(self, option_list):
		cmd = ['meson', 'configure' if self.configured else 'setup']
		cmd += self.trailing
		if self.backend:
			cmd.extend(['--backend', self.backend])
		cmd += get_darguments(option_list)
		cmd.append(self.builddir)
		if not self.configured:
			cmd.append(self.sourcedir)
		
		layout = LayoutCommandOutput(cmd, self.main_loop)
		urwid.connect_signal(layout, 'back', self.back_to_option_list)
		self.main_loop.widget = layout
	
	def back_to_option_list(self, terminal):
		if terminal.successful():
			self.configured = True
		self.main_loop.widget = self.layout_option_list