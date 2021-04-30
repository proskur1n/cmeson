import urwid
import os
from signal import SIGCONT, SIGTSTP, SIG_DFL

"""
By default, urwid.raw_display.Screen does not restore the alternative screen on
ctrl-z (SIGTSTP) and simply leaves the terminal window in a mess. This wrapper
can be removed after urwid fixes this problem.
"""
class Screen(urwid.raw_display.Screen):
	def _sigtstp_handler(self, signum, frame=None):
		self.stop() # calls signal_restore
		self.signal_handler_setter(SIGCONT, self._sigcont_handler)
		os.kill(os.getpid(), SIGTSTP)

	def _sigcont_handler(self, signum, frame=None):
		# don't remove this call, as doing so breaks ctrl-z -> bg -> fg
		self.signal_handler_setter(SIGCONT, SIG_DFL)
		self.start() # calls signal_init
		self._sigwinch_handler(None, None)

	def signal_init(self):
		super().signal_init()
		self.signal_handler_setter(SIGTSTP, self._sigtstp_handler)

	def signal_restore(self):
		super().signal_restore()
		self.signal_handler_setter(SIGTSTP, SIG_DFL)
