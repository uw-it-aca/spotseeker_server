#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/management/commands/Makefile.am $
#	$Revision: 33440 $ $Date: 2013-01-04 13:32:51 -0600 (Fri, 04 Jan 2013) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	createsecretkey.py

COMPILED		= __init__.pyc	createsecretkey.pyc

moduledir		= $(pythondir)/sdg/django/management/commands

module_DATA		= $(COMPILED)

SUBDIRS			= 

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
