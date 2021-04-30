import urwid
import os

class CommandViewer(urwid.Terminal):
	def __init__(self, command, main_loop):
		self.returncode = None
		super().__init__(command, main_loop=main_loop)

	"""
	urwid.Terminal does not support querying the return code of a command. This
	wrapper stores the return code as `self.returncode`
	"""
	def terminate(self):
		if self.terminated:
			return
		self.terminated = True
		self.remove_watch()
		self.change_focus(False)
		if self.pid:
			_, status = os.waitpid(self.pid, 0)
			self.returncode = status >> 8
			os.close(self.master)
	
	"""
	Resizing urwid.Terminal results in an exception if the running command has
	terminated. This wrapper fixes this behavior.
	"""
	def render(self, size, focus=False):
		width, height = size
		resized = width != self.width or height != self.height
		if self.terminated and resized:
			self.term.resize(width, height)
			self.width = width
			self.height = height
		return super().render(size, focus)
	
	"""
	Allows the main application to respond to ctrl-z and other tty events
	that are unmapped by default urwid.Terminal.change_focus() call.
	"""
	def change_focus(self, has_focus):
		if self.terminated:
			return
		self.has_focus = has_focus
		if self.term is not None:
			self.term.has_focus = has_focus
			self.term.set_term_cursor()

	def keypress(self, size, key):
		if key in ('up', 'down'):
			if self.term:
				self.term.scroll_buffer(key == 'up', lines=1)
			return
		return super().keypress(size, key)
	
	def successful(self):
		if not self.terminated:
			raise ValueError('command not yet terminated')
		return self.returncode == 0

class LayoutCommandOutput(urwid.Pile):
	signals = ['back']

	def __init__(self, command, main_loop):
		self.main_loop = main_loop
		self.term = CommandViewer(command, main_loop)
		urwid.connect_signal(self.term, 'closed', self.on_closed)
		self.footer = urwid.Text('')
		super().__init__([
			self.term,
			(urwid.PACK, urwid.Divider()),
			(urwid.PACK, self.footer),
		])
	
	def on_closed(self, term):
		if term.successful():
			items = ['[q] quit', '[b] back']
		else:
			items = ['[b] back']
		self.footer.set_text('   '.join(items))
	
	def keypress(self, size, key):
		if not super().keypress(size, key):
			return
		if not self.term.terminated:
			return key
		if key == 'b':
			urwid.emit_signal(self, 'back', self.term)
			return
		if self.term.successful() and key == 'q':
			raise urwid.ExitMainLoop()
		return key