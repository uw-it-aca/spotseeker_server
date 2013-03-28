#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/Makefile.am $
#	$Revision: 33502 $ $Date: 2013-01-15 11:31:40 -0600 (Tue, 15 Jan 2013) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	admin.py	\
			  context_processors.py

COMPILED		= __init__.pyc	admin.pyc	\
			  context_processors.pyc

moduledir		= $(pythondir)/sdg/django

module_DATA		= $(COMPILED)

SUBDIRS			= auth bluestem handoff management settings

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
