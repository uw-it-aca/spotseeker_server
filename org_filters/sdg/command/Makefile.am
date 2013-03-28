#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/command/Makefile.am $
#	$Revision: 23671 $ $Date: 2011-05-26 16:16:52 -0500 (Thu, 26 May 2011) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	\
			  make_service_secret.py	\
			  prune_handoff_session.py

COMPILED		= __init__.pyc	\
			  make_service_secret.pyc	\
			  prune_handoff_session.pyc

moduledir		= $(pythondir)/sdg/command

module_DATA		= $(COMPILED)

SUBDIRS			= 

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<', '$@', doraise=True)"
