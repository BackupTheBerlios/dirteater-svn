#!/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__revision__ = "$Id$"
__headurl__ = "$HeadURL$"

import os
import sys
import signal
import string
import threading
import pprint

import xml.dom.minidom
from xml.dom.minidom import Node
from xml.dom.minidom import Element

def main():
	# Some globals and variables
	global config

	config = {}

	options = [
		"--config",		"--configdump",
		"--debug",
		"--verbose",	"--version"
	]
	shortoptions = {
		"c":"--config",
		"d":"--debug",
		"v":"--verbose",
		"V":"--version"
	}

	# Scan for commandline options. This is like the handling 
	# of Gentoo's (http://www.gentoo.org) "emerge". 
	# Thanks guys!
	
	tmpcmd = sys.argv[1:]
	cmd = []
	opts = []
	for x in tmpcmd:
		if x[0:1] == "-" and x[1:2] != "-":
			for y in x[1:]:
				if shortoptions.has_key(y):
					if shortoptions[y] in cmd:
						print "*** Warning: Redundant use of "+shortoptions[y]
					else:
						cmd.append(shortoptions[y])
				else:
					print "!!! Error: -"+y+" is an invalid option."
					sys.exit(1)
		else:
			cmd.append(x)
	for x in cmd:
		if len(x) >= 2 and x[0:2] != "--":
			opts.append(x)
		elif len(x) >= 2 and x[0:2] == "--":
			opts.append(x)
		elif x not in options:
			print "!!! Error: "+x+" is an invalid option."
			sys.exit(1)

	# "One option, one Output and die" (tm)
	if "--help" in opts: 
		print "I guess you need help. That's bad at the moment! ;)"
		sys.exit()
	elif "--version" in opts:
		# Some easy release-checkin'
		headinfo = string.split(__headurl__, "/")
		if "tags" in headinfo:
			print "Stable release: "+headinfo[headinfo.index("tags")+1]
		else:
			print "This is a development version. Expect bugs!"
			print __revision__
		sys.exit()
	
	# Read the static configuration and ensure that commandline options
	# have a higher priority than config.xml options.
	conffile = xml.dom.minidom.parse("config.xml")
	
	general_config = conffile.getElementsByTagName('general')
	for node in general_config:
		for general in node.childNodes:
			if general.nodeType == Node.ELEMENT_NODE:
				setname = general.nodeName
			for set in general.childNodes:
				config[setname] = set.data
	
	if "--configdump" in opts:
		pprint.pprint(config)

if __name__ == "__main__":
	main()
