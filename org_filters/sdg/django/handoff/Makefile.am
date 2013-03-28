#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/handoff/Makefile.am $
#	$Revision: 26372 $ $Date: 2011-10-11 14:56:21 -0500 (Tue, 11 Oct 2011) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	_wsapi.py	models.py

COMPILED		= __init__.pyc	_wsapi.pyc	models.pyc

moduledir		= $(pythondir)/sdg/django/handoff

module_DATA		= $(COMPILED)

SUBDIRS			= 

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
