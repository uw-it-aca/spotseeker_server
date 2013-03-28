#	$URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/Makefile.am $
#	$Revision: 31262 $ $Date: 2012-07-17 12:47:23 -0500 (Tue, 17 Jul 2012) $

CLEANFILES 		= $(COMPILED)

EXTRA_DIST 		= __init__.py	attrdict.py	\
			  config.py	directory.py	\
			  hexdigest.py	standard_path.py

COMPILED		= __init__.pyc	attrdict.pyc	\
			  config.pyc	directory.pyc	\
			  hexdigest.pyc	standard_path.pyc

moduledir		= $(pythondir)/sdg

module_DATA		= $(COMPILED)

SUBDIRS			= command django log ws

%.pyc: %.py
	@echo "compiling $(subdir)/$<"
	@${PYTHON} -c "import py_compile; py_compile.compile('$<' , '$@', doraise=True)"
