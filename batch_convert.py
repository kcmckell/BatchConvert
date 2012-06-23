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
-+ Soft light 19
-+ Screen 4
-+ Multiply 3
-+ Lighten only 10 (mapped to Lighten) 
-+ Hue 11
-+ Hard light 18
-+ Difference 6
-+ Darken only 9 (mapped to Darken)
-+ Color 13
+ Unsupported layer modes:
-+ Divide
--+ Close: Invert top, top mode set to Screen.
--+ Not so fast: Close for one test case, not close for another.  Not a good substitute.
-+ Dodge
-+ Burn
-+ Grain extract
-+ Grain Merge
-+ Addition
-+ Subtraction
+ Differeing layer modes:
-+ Overlay 
--+ Close, but dissimilar definitions.
--+ Ref: https://bugzilla.gnome.org/show_bug.cgi?id=162395
--+ Photoshop Overlay is equivalent to Gimp layer swap, top layer Hard Light.
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
import os, glob, time, copy
from stat import *

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
Globals
"""
layer_modes = ['Normal','Dissolve','Behind','Multiply','Screen','Overlay','Difference','Addition','Subtract','Darken Only','Lighten Only','Hue','Saturation','Color','Value','Divide','Dodge','Burn','Hardlight','Softlight','Grain Extract','Grain Merge','Color Erase','Erase','Replace','Anti Erase'];
layer_modes_dict = dict(zip(xrange(len(layer_modes)),layer_modes));

class JumpList (list):
	"""
	Shortcut for jumping to next and previous elements of a list.
	NOTE: Not designed for lists with repeated entries.
	NOTE: Next of last element returns None; Prev of first element returns None.
	>>> v = JumpList([0,1,2,3]);
	>>> v.next(1)
	2
	>>> v.prev(1)
	0
	"""
	def next(self,element):
		elin = self.index(element);
		N = len(self);		
		if elin >= N-1: return None;
		return self[self.index(element)+1]
	def prev(self,element):
		elin = self.index(element);
		N = len(self);
		if elin == 0: return None;
		return self[self.index(element)-1]

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
#		pdb.gimp_message("And another one.")
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
	# Timestamp mangling
	st = os.stat(filepathnames)
	orig_atime = st[ST_ATIME]; # Windows does not render ATIME (date accessed).
	orig_mtime = st[ST_MTIME]; # Windows renders MTIME as Date Modified.
	os.utime(newname,(orig_atime,orig_mtime)); # Python cannot modify Date Created.  Must settle for Date Modified only.
	
	
def layer_mod( image_object ):
	"""
	Modifies layers in the IMAGE as necessary to make them PSD-compliant.
	"""
	# Separate "good" layer modes from "bad" ones.
	layerModeJudgement = {'good' : [19,4,3,10,11,18,6,9,13]};
	img = image_object;
	layerActive = pdb.gimp_image_active_drawable(img);
	layerlist = JumpList(img.layers);
	layerlist.reverse();	# Bottom layer is now at list index 0.
	Nlayers = len(layerlist);
	origPosition = {};
	origVisibility = {0:[], 1:[]};
	origMode = dict(zip(xrange(len(layer_modes)), [[] for x in xrange(len(layer_modes))]));
	for lay in layerlist:
		pos = pdb.gimp_image_get_layer_position(img,lay);
		origPosition[pos] = lay;
		if pdb.gimp_drawable_get_visible(lay) == 1:
			origVisibility[1].append(lay);
		else:
			origVisibility[0].append(lay);
		origMode[pdb.gimp_layer_get_mode(lay)].append(lay);
	newPosition = copy.deepcopy(origPosition);
	newVisibility = copy.deepcopy(origVisibility);
	newMode = copy.deepcopy(origMode);
	[pdb.gimp_drawable_set_visible(k,0) for k in layerlist];
	for lay in layerlist:
		# If layer is text, convert to RGBA layer.
		if pdb.gimp_drawable_is_text_layer(lay):
			laypos = pdb.gimp_image_get_layer_position(img, lay);
			pdb.gimp_drawable_set_visible(lay,1);
			newlay = pdb.gimp_layer_new_from_visible(img, img, lay.name+"[Text]");
			pdb.gimp_image_add_layer(img, newlay, laypos);
			if lay == layerActive:
				layerActive = newlay;
			img.remove_layer(lay);
			newPosition[laypos] = newlay;
			for k,v in newVisibility.iteritems():
				if lay in v:
					v.remove(lay);
					v.append(newlay);
			for k,v in newMode.iteritems():
				if lay in v:
					v.remove(lay);
					v.append(newlay);
			pdb.gimp_drawable_set_visible(newlay,0);
		# end if text
	layerlist = JumpList(img.layers);
	layerlist.reverse();
	for lay in layerlist[:]:
		# If layer mode is not supported well by the Save to PhotoShop function, Make new layer from visible.
		nextLay = layerlist.next(lay);
		if (pdb.gimp_layer_get_mode(lay) not in layerModeJudgement['good']) & ((not nextLay) or (pdb.gimp_layer_get_mode(nextLay) in layerModeJudgement['good'])):
			newName = lay.name+"[BadMode:"+layer_modes_dict[pdb.gimp_layer_get_mode(lay)]+"]";
			# Turn on this layer and all below.
			visLayers = [];
			for p in range(0,1+layerlist.index(lay)):
				if layerlist[p] in newVisibility[1]: 
					visLayers.append(layerlist[p]);
			[pdb.gimp_drawable_set_visible(L,1) for L in visLayers];
			# Make new layer from visible.
			newlay = pdb.gimp_layer_new_from_visible(img, img, newName);
			if lay in origVisibility[1]: 
				newVisibility[1].append(newlay);
			else:
				newVisibility[0].append(newlay);
			newMode[0].append(newlay);
			oldPos = pdb.gimp_image_get_layer_position(img, lay)
			pdb.gimp_image_add_layer(img, newlay, oldPos);
			layerlist.reverse();
			layerlist.insert(oldPos, newlay);
			layerlist.reverse();
#			# Turn off this layer and all below.
##			[pdb.gimp_drawable_set_visible(L,0) for L in visLayers.append(newlay)];
#			pdb.gimp_drawable_set_visible(newlay,0);
#			[pdb.gimp_drawable_set_visible(L,0) for L in visLayers];
#				# Remember: layer position starts at 0 on top.  Inserting a layer at position x will add one to the position of every layer that was formerly >= x.
#				# Also remember, you've reversed the order of layerlist.
		# end if bad layer mode.
	for k,v in newVisibility.iteritems():
		[pdb.gimp_drawable_set_visible(layer,k) for layer in v];
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
