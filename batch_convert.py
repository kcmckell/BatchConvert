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

"""
TODO:
+ Convert text to layer
+ Unsupported layer modes:
-+ Divide not offered in PS => Should be able to invert top layer then multiply.

-+ Grain Merge
-+ Other grain?
-+ Gimp Overlay => Invert layer position+ Hard light
ref: http://emptyeasel.com/2008/10/31/explaining-blending-modes-in-photoshop-and-gimp-multiply-divide-overlay-screen/
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
Template_batch_help = "Batch convert XCF to PSD in all subdirectories."                              
Template_batch_description = "Python-fu plugin Gimp 2.6."+" "+Template_batch_help

"""
Main
"""                                      
def python_fu_batch_convert( dirname, ext ):
	"""
	Main wrapper function designed to look for appropriate files and send them to GIMP for conversion.
	INPUTS:
	dirname - String with path to root directory.  Input from GUI.
	ext - String with file extension ('xcf', for example).
	OUTPUT:
	Confirmation window.
	"""
	L = walk_with_me( dirname, ext)
	numFilesFound = 0;
	for f in L:
		numFilesFound += 1;
		pdb.gimp_message("And another one.")
		# Start of process
		process_files( f );
		# End of process
##		print '===='
##		print f
	if numFilesFound == 0:
		pdb.gimp_message( _("%s has no files to convert") %(dirname ));
	else:
		pdb.gimp_message( "We found {0} files to convert.  Have a nice day.".format(numFilesFound));

def walk_with_me( dirname, ext ):
	"""
	Wrapper to walk from root DIRNAME and return generator with all files ending in *.EXT
	"""
	root = u''+dirname;
	if os.path.exists( root ):
		globpattern = '*.'+ext;
		for path, dirs, files, in os.walk(os.path.abspath(root)):
			G = glob.glob(os.path.join(path,globpattern));
			if G:
				for filename in G:
					yield os.path.join(path,filename);
	else:
		pdb.gimp_message( _("%s don't exist") %(dirname) )

def process_files( filepathnames ): 
	"""
	Contains process to be applied to each image file found in WALK_WITH_ME.
	"""
	#write here the batch process
	image = pdb.gimp_file_load(filepathnames,filepathnames);
	
	
	
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

##def test():
##	python_fu_batch_convert( 'C:\\Users\\Clay\\Pictures', 'ballsack' );

##if __name__ == '__main__':
##	test()

main()	
