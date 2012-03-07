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
Super useful gimpfu reference: http://www.jamesh.id.au/software/pygimp/gimp-objects.html
"""

"""
TODO:
DONE Convert text to layer
Jeez:
http://www.pegtop.net/delphi/articles/blendmodes/softlight.htm

+ Good to go:
-+ Soft light
-+ Screen
-+ Overlay ??? https://bugzilla.gnome.org/show_bug.cgi?id=162395
-+ Multiply
-+ Lighten only
-+ Hue
-+ Hard light
-+ Difference
-+ Darken only
-+ Color
+ Unsupported layer modes:
-+ Divide
--+ Close: Invert top, top mode set to Screen.
-+ Dodge
-+ Burn
-+ Grain extract
-+ Grain Merge
-+ Addition
-+ Subtraction
+ Differeing layer modes:
-+ Value
-+ Saturation
--+ Photoshop decomposes into Hue, Chroma, Luma.  
--+ GIMP decomposes to HSV.
--+ Photoshop "saturation" suppresses top layer's H and L and displays {B_H, T_C, B_L}.
--+ GIMP saturation suppress top layer's H and V and displays {B_H, T_S, B_V}.
--+ Photoshop equivalent of "value" suppresses top layer's H and C and displays {B_H, B_C, T_L}.
--+ GIMP value suppresses top layer's H and S and displays {B_H, B_S, T_V}.
--+ Haven't found transformations f1 and f2 such that {f1(B)_H, f2(T)_C, f1(B)_L} = {B_H, T_S, B_V} (for saturation mode, e.g.)
refs: http://en.wikipedia.org/wiki/Blend_modes
refs: http://en.wikipedia.org/wiki/HSL_and_HSV#Hue_and_chroma
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
	# Check for layer modifications.
	(imageModified, activeLayer) = layer_mod(image);
	#DONE: Which serialization works in PS (MSB or LSB)?
	#---- All are openable, editable in PS, and recognized by LR.  Doesn't matter.
	#DONE: Which compression?
	#---- All identical.  856MB test XCF is same size in all three compressions.
	# Save out to same path as original, but convert extension.
	(filepath,basefilename) = os.path.split( filepathnames );
	(shortname, extension) = os.path.splitext(basefilename);
	newname = os.path.join(filepath,shortname+os.extsep+'psd');
	pdb.file_psd_save(imageModified, activeLayer, newname, newname, 0, 0);
	
	
def layer_mod( image_object ):
	"""
	Modifies layers in the IMAGE as necessary to make them PSD-compliant.
	"""
	img = image_object;
	layerActive = pdb.gimp_image_active_drawable(img);
	layerlist = img.layers;
	numlayers = len(layerlist);
	origVisibility = [pdb.gimp_drawable_get_visible(lay) for lay in layerlist];
	for lay in layerlist:
		# If layer is text, convert to RGBA layer.
		if pdb.gimp_drawable_is_text_layer(lay):
			laypos = pdb.gimp_image_get_layer_position(img, lay);
			for k in layerlist:
				if k == lay:
					pdb.gimp_drawable_set_visible(k,1);
				else:
					pdb.gimp_drawable_set_visible(k,0);
			newlay = pdb.gimp_layer_new_from_visible(img, img, lay.name);
			pdb.gimp_image_add_layer(img, newlay, laypos);
			if lay == layerActive:
				layerActive = newlay;
			pdg.gimp_drawable_delete(lay);
		# end if text
	return (img, layerActive);
	
	
	
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
