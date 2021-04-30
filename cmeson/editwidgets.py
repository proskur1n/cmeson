import urwid

class ComboEdit(urwid.SelectableIcon):
	def __init__(self, choices, value):
		super().__init__('')
		self._choices = choices
		self.set_value(value)
	
	def choice_index(self, value):
		idx = self._choices.index(value)
		if idx < 0:
			raise ValueError('choices do not contain "{}"'.format(value))
		return idx
	
	def get_value(self):
		return self._choices[self._selection]
	
	def set_value(self, value):
		self._selection = self.choice_index(value)
		self.set_text(str(value))
	
	def keypress(self, size, key):
		if key != 'enter':
			return key
		self._selection += 1
		self._selection %= len(self._choices)
		self.set_value(self._choices[self._selection])

class StringEdit(urwid.Edit):
	def __init__(self, value):
		self.editing = False
		super().__init__(edit_text=str(value))
	
	def get_value(self):
		return self.get_edit_text()
	
	def set_value(self, value):
		self.set_edit_text(str(value))
	
	def keypress(self, size, key):
		if key == 'enter':
			self.editing = not self.editing
		elif key == 'esc':
			self.editing = False
		elif self.editing:
			return super().keypress(size, key)
		else:
			return key

class BooleanEdit(ComboEdit):
	def __init__(self, value):
		super().__init__(['false', 'true'], str(value).lower())

class IntegerEdit(StringEdit):
	pass

class ArrayEdit(StringEdit):
	pass

def get_edit_widget(option):
	_type = option['type']
	value = option['value']
	types = {
		'string': StringEdit,
		'boolean': BooleanEdit,
		'integer': IntegerEdit,
		'array': ArrayEdit
	}
	if _type == 'combo':
		return ComboEdit(option['choices'], value)
	if _type not in types:
		return StringEdit(value)
	return types[_type](value)

class OptionEdit(urwid.Columns):
	def __init__(self, max_name_len, option):
		self.name = option['name']
		self.section = option['section']
		self.description = option['description']
		self.edit_widget = get_edit_widget(option)
		self.original_value = self.edit_widget.get_value()
		items = [
			(max_name_len, urwid.Text(self.name)),
			self.edit_widget
		]
		super().__init__(items, dividechars=10)
	
	def get_value(self):
		return self.edit_widget.get_value()
	
	def set_value(self, value):
		self.edit_widget.set_value(value)
	
	def changed(self):
		return self.get_value() != self.original_value
	
	def keypress(self, size, key):
		if not self.edit_widget.keypress(size, key):
			return
		if key == 'u':
			self.set_value(self.original_value)
		else:
			return key
	
	def on_focus_lost(self):
		if hasattr(self.edit_widget, 'editing'):
			self.edit_widget.editing = False
