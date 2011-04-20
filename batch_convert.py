#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Batch conversion for Gimp 2.11
(cc) K. Clay McKell 2011

Created with help from:
Template-batch python-fu by Raymond Ostertag

Installation : put the template-batch.py file in your $HOME/.gimp-2.n/plug-ins.
On Linux and Mac OSX the file must be executable.
Documentation : http://www.gimp.org/docs/python/index.html
"""

from gimpfu import *
import os, glob

"""
Internationalization:
i18n
"""
import gettext
locale_directory = gimp.locale_directory
gettext.install( "gimp20-template" , locale_directory, unicode=True )

"""
Descriptors
"""
Template_batch_help = _("Batch convert XCF to PSD in all subdirectories.")                                
Template_batch_description = _("Python-fu plugin Gimp 2.6.")+" "+Template_batch_help

"""
Main
"""                                       
def process_files( filepathnames ): 
	#write here the batch process
	pdb.gimp_message( _("The selected directory has %s files to handle") %(str( len( filepathnames ))));

def python_fu_batch_convert( dirname, ext ):
	if os.path.exists( u''+dirname ):
		globpattern = u''+dirname + os.sep + '*.' + ext
		filepathnames = glob.glob( globpattern ) # return complete path name of files
		if filepathnames:
			#Start of process
			process_files( filepathnames );
			# End of process         
		else:
			pdb.gimp_message( _("%s don't have files to handle") %(dirname ))      
	else:
		pdb.gimp_message( _("%s don't exist") %(dirname) )

"""
Register
"""
register(
 	"python_fu_batch_convert",
	Template_batch_description,
	Template_batch_help,
	"K. Clay McKell",
	"GPL License",
	"2011",
	_("Batch Convert"),
	"",
	[
		(PF_DIRNAME, "directory", _("Directory"), os.getcwd() ),
		(PF_STRING, "ext", _("File extension"), "jpg" ),
	],
	[],
	python_fu_batch_convert,
	menu="<Image>/File",
	domain=("gimp20-template", locale_directory)   
	)

main()
