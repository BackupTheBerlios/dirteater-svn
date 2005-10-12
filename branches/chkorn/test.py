#!/usr/bin/env python

# Bugs
#
# - mehrfach vorkommendes wird vom aktuellsten ueberschrieben
# - attribute + text geht nicht gleichzeitig
# - 3-dimensional geht nicht

import sys, pprint
from elementtree.ElementTree import ElementTree
root = ElementTree(file='dirt.xml')
iter = root.getiterator()

config = {}
lasttag = []
lastvalue = []

for element in iter:
	#if element.keys():
	#	tempdict = {}
	#	for name, value in element.items():
	#		tempdict[name] = value
	#	config[element.tag] = tempdict
	#if element.text and element.text.strip() != "":
	#	text = element.text
	#	config[element.tag] = element.text
	if element.getchildren():
		if not element.keys():
			config[element.tag] = "NOCHWAS"
		for child in element:
			if config.has_key(child.tag):
				print child.tag, "sollte ein dict werden"
			#else: 
			config[child.tag] = child.text
			#print "Tag '",child.tag,"'", child.text
			if child.getchildren():
				lasttag.append(child.tag)
				lastvalue.append(child.text)
			else:
			
			#if child.tail and child.tail.strip() != "":
			#	text = child.tail
			#	print "\t\t7__Text:", repr(text)  


print "\n\n"
pprint.pprint(config)
