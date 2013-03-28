#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/log/Makefile.am $
#	$Revision: 26373 $ $Date: 2011-10-11 15:30:33 -0500 (Tue, 11 Oct 2011) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	levels.py

COMPILED		= __init__.pyc	levels.pyc

moduledir		= $(pythondir)/sdg/log

module_DATA		= $(COMPILED)

SUBDIRS			= 

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<' , '$@', doraise=True)"
