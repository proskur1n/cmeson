import urwid
import subprocess
import json
import getopt
import sys
from LayoutCommandOutput import LayoutCommandOutput
from LayoutOptionList import LayoutOptionList

usage = """\
cmeson [OPTIONS] builddir [sourcedir] [TRAILING]

cmeson is a TUI for meson build system

  -h, --help           Show this message and exit
  --backend BACKEND    Select backend to query build options for. See meson
                       documentation for possible BACKEND values

TRAILING options are passed as-is to 'meson setup' or 'meson configure'
"""

def pop_non_argument(trailing):
	if trailing[0].startswith('-'):
		raise IndexError
	return trailing.pop(0)

class ApplicationError(Exception):
	pass

class Application:
	palette = [
		('selected', 'bold,standout', ''),
		('description', 'bold,standout', '')
	]

	def __init__(self, argv):
		self.parse_arguments(argv)
		self.configured = self.is_configured_project()
		layout = LayoutOptionList(self.get_build_options())
		urwid.connect_signal(layout, 'configure', self.configure_meson)
		self.layout_option_list = layout
		self.main_loop = urwid.MainLoop(layout, self.palette, handle_mouse=False)
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

	"""
	A hacky way to find out if we should run 'meson setup' or 'meson configure'
	when configuring the project
	"""
	def is_configured_project(self):
		cmd = ['meson', 'introspect', '--projectinfo', self.builddir]
		return subprocess.call(
			cmd,
			stderr=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL) == 0

	# TODO unhelpful error message
	def get_build_options(self):
		path = self.builddir if self.configured else self.sourcedir + '/meson.build'
		cmd = ['meson', 'introspect', '--buildoptions']
		cmd += ['--backend', self.backend] if self.backend else []
		cmd += [path]

		try:
			json_str = subprocess.check_output(cmd)
		except subprocess.CalledProcessError:
			msg = 'meson returned non-zero exit code\n' + ' '.join(cmd)
			raise ApplicationError(msg)
		
		return json.loads(json_str)
	
	"""
	dargument = -D argument

	Returns list of darguments ['-Da=b', '-Dc=d', ...] for build options that
	have changed and need to be reconfigured
	"""
	@staticmethod
	def get_darguments(option_list):
		widgets = map(lambda x: x[0], option_list.build_options())
		changed = filter(lambda x: x.changed(), widgets)
		dargs = []
		for widget in changed:
			darg = '-D{}={}'.format(widget.name, widget.get_value())
			dargs.append(darg)
		return dargs
	
	def configure_meson(self, option_list):
		cmd = ['meson', 'configure' if self.configured else 'setup']
		cmd += self.trailing
		cmd += ['--backend', self.backend] if self.backend else []
		cmd += self.get_darguments(option_list)
		cmd += [self.builddir]
		cmd += [] if self.configured else [self.sourcedir]
		
		layout = LayoutCommandOutput(cmd, self.main_loop)
		urwid.connect_signal(layout, 'back', self.back_to_option_list)
		self.main_loop.widget = layout
	
	def back_to_option_list(self, terminal):
		if terminal.successful():
			self.configured = True
		self.main_loop.widget = self.layout_option_list

if __name__ == '__main__':
	try:
		app = Application(sys.argv)
	except ApplicationError as e:
		sys.exit('cmeson: ' + str(e))