#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/settings/Makefile.am $
#	$Revision: 33485 $ $Date: 2013-01-11 17:02:16 -0600 (Fri, 11 Jan 2013) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	\
			  _util.py	standard.py

COMPILED		= __init__.pyc	\
			  _util.pyc	standard.pyc

moduledir		= $(pythondir)/sdg/django/settings

module_DATA		= $(COMPILED)

SUBDIRS			= 

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
