cmeson is a text-based user interface for the [meson](https://mesonbuild.com/) build system and offers a convenient, graphical way to configure build options instead of having to memorize and type them out in the terminal. Due to incompatibility of its TUI library, cmeson only supports Linux, MacOS and other Unix-like systems. Consequently, if you want to use this application on Windows, you can do so through WSL or Cygwin. The name and functionality of this application are derived from a similar application for [cmake](https://cmake.org/) ccmake.

![showcase.png](https://raw.githubusercontent.com/proskur1n/cmeson/master/docs/showcase.png "cmeson showcase")

# Installation

From PyPI:
	
	pip3 install --user cmeson

From source:

	git clone https://github.com/proskur1n/cmeson
	cd cmeson
	pip3 install --user .

# Usage

	cmeson builddir
	cmeson [OPTIONS] builddir [sourcedir] [TRAILING]

	OPTIONS
		-h, --help               Show help message and exit
		--backend BACKEND        Select backend to query build options for

**sourcedir** is a directory containing *meson.build* file and **builddir** is the build directory for the project. **sourcedir** is only needed for projects for which *meson setup* has not been run yet and defaults to the current working directory if not specified.

The **--backend** option determines the list of options in the backend section and defaults to ninja. If you specify a backend using this option, you must not change the backend in TUI as this will result in an error from meson. See the meson documentation for a complete list of supported backends.

If any trailing options are given, they are passed as-is to meson and are not interpreted by this application. Normally you do not need to specify any trailing options as most of them can be configured directly through TUI.

# License

MIT License (see LICENSE for more information)