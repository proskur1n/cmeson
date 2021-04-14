import urwid
import itertools
from .editwidgets import OptionEdit

def heading(title, div_char=u'─'):
	line = urwid.Divider(div_char)
	text = urwid.Text(title.upper())
	return urwid.Columns([
		(12, line),
		(urwid.PACK, text),
		line,
	], dividechars=1)

class SearchField(urwid.Edit):
	signals = ['cancel', 'search']

	def keypress(self, size, key):
		if key not in ('enter', 'esc'):
			super().keypress(size, key)
			return
		if key == 'enter' and self.edit_text != '':
			urwid.emit_signal(self, 'search', self.edit_text)
			return
		urwid.emit_signal(self, 'cancel')

def option_list_footer():
	items = [
		'[enter] edit',
		'[u] undo',
		'[/] search',
		'[q] discard and quit',
		'[c] configure',
	]
	return urwid.Text('   '.join(items))

def group_into_sections(widgets):
	order = ['user', 'compiler', 'core', 'base', 'test', 'backend', 'directory']
	widgets.sort(key=lambda x: order.index(x.section))
	groups = itertools.groupby(widgets, lambda x: x.section)
	items = []
	for section, matching in groups:
		items.append(heading(section))
		items.extend(matching)
	return items

class OptionList(urwid.ListBox):
	def __init__(self, options):
		max_name_len = max(len(x['name']) for x in options)
		widgets = [OptionEdit(max_name_len, x) for x in options]
		grouped = group_into_sections(widgets)
		decorated = [urwid.AttrMap(x, '', 'selected') for x in grouped]
		super().__init__(urwid.SimpleFocusListWalker(decorated))
	
	def change_focus(self, *args, **kwargs):
		if self.focus:
			self.focus.original_widget.on_focus_lost()
		super().change_focus(*args, **kwargs)
	
	"""
	Iterates over all selectable widgets, starting with the focused one if
	`reverse == False` and the previous widget otherwise
	"""
	def build_options(self, reverse=False):
		if len(self.body) == 0:
			return
		focus = self.focus_position or 0
		positions = self.body.positions(reverse)
		for pos in positions:
			index = (focus + pos) % len(self.body)
			widget = self.body[index].original_widget
			if widget.selectable():
				yield widget, index
	
	def find_next(self, query, reverse=False):
		_, current = self.body.get_focus()
		for widget, position in self.build_options(reverse):
			if widget.name.find(query) >= 0 and position != current:
				self.set_focus(position)
				return widget, position

class LayoutOptionList(urwid.Pile):	
	signals = ['configure']

	def __init__(self, options):
		self.last_search_query = ''
		self.option_list = OptionList(options)
		urwid.connect_signal(self.option_list.body, 'modified', self.update_description)
		self.description = urwid.Text('')
		self.footer = urwid.WidgetPlaceholder(option_list_footer())
		super().__init__([
			self.option_list,
			(urwid.PACK, urwid.Divider()),
			(urwid.PACK, urwid.AttrMap(self.description, 'description')),
			(urwid.PACK, self.footer),
		])
	
	def keypress(self, size, key):
		if not super().keypress(size, key):
			return
		if key == 'q':
			raise urwid.ExitMainLoop()
		if key == '/':
			self.open_search_field()
			return
		if key in ('n', 'N'):
			self.option_list.find_next(self.last_search_query, key == 'N')
			return
		if key == 'c':
			urwid.emit_signal(self, 'configure', self.option_list)
			return
		return key
	
	def open_search_field(self):
		sf = SearchField('search: ')
		urwid.connect_signal(sf, 'cancel', self.close_search_field)
		urwid.connect_signal(sf, 'search', self.perform_search)
		self.footer.original_widget = sf
		self.focus_position = len(self.contents) - 1
	
	def close_search_field(self):
		self.footer.original_widget = option_list_footer()
		self.focus_position = 0
	
	def perform_search(self, query):
		self.close_search_field()
		self.option_list.find_next(query)
		self.last_search_query = query
	
	def update_description(self):
		focus = self.option_list.focus
		text = ''
		if focus:
			widget = focus.original_widget
			text = widget.description
		self.description.set_text(text)