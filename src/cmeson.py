import urwid
import subprocess
import json

from LayoutCommandOutput import LayoutCommandOutput
from LayoutOptionList import LayoutOptionList

def is_configured_project():
	# TODO
	return False

def get_build_options():
	if is_configured_project():
		path = builddir
	else:
		path = sourcedir + "/meson.build"
	cmd = ["meson", "introspect", path, "--buildoptions"]
	json_str = subprocess.check_output(cmd)
	return json.loads(json_str)

builddir = "seatd/build"
sourcedir = "seatd"

palette = [
	('selected', 'bold,standout', ''),
]

main_loop = urwid.MainLoop(None, palette)
# top = LayoutCommandOutput("ls -a wh0w3h0o".split(), main_loop)
opts = get_build_options()
top = LayoutOptionList(opts)
main_loop.widget = top
main_loop.run()

num = 0
for widget, _ in top.option_list.build_options(True):
	print(widget.name)
	num = num + 1
print(num)
print(len(opts))