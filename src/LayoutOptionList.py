import urwid
from OptionEdit import OptionEdit

def option_list_footer():
	items = [
		"[enter] edit",
		"[u] undo",
		"[q] discard and quit",
		"[c] configure",
	]
	return urwid.Text("   ".join(items))

# TODO
class Heading(urwid.Text):
	def __init__(self, name):
		super().__init__('----' + name.upper() + '-' * 80)

def split_into_sections(widgets):
	order = ['user', 'compiler', 'core', 'base', 'test', 'backend', 'directory']
	items = []
	for section in order:
		matches = [x for x in widgets if x.section == section]
		items.append(Heading(section))
		items.extend(matches)
	unknown = [x for x in widgets if x.section not in order]
	if len(unknown):
		items.append(Heading('unknown'))
		items.extend(unknown)
	return items

class OptionList(urwid.ListBox):
	def __init__(self, options):
		max_name_len = max([len(x['name']) for x in options])
		items = [OptionEdit(max_name_len, x) for x in options]
		sorted_items = split_into_sections(items)
		walker = urwid.SimpleFocusListWalker(sorted_items)
		super().__init__(walker)
	
	def change_focus(self, size, position, *args):
		if self.focus:
			self.focus.on_focus_lost()
		super().change_focus(size, position, *args)

class LayoutOptionList(urwid.Pile):
	def __init__(self, options):
		self.option_list = OptionList(options)
		footer = option_list_footer()
		super().__init__([
			self.option_list,
			(urwid.PACK, urwid.Divider()),
			# TODO
			# (urwid.PACK, description),
			(urwid.PACK, footer),
		])
	
	def keypress(self, size, key):
		if not super().keypress(size, key):
			return
		if key == 'q':
			raise urwid.ExitMainLoop()
		return key