#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/management/Makefile.am $
#	$Revision: 33440 $ $Date: 2013-01-04 13:32:51 -0600 (Fri, 04 Jan 2013) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py

COMPILED		= __init__.pyc

moduledir		= $(pythondir)/sdg/django/management

module_DATA		= $(COMPILED)

SUBDIRS			= commands

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
