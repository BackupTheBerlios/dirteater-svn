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
import types
import string
import threading
import os.path
import pprint
import xml.dom.minidom

from xml.dom.minidom import Node
from xml.dom.minidom import Element
from xml.parsers.xmlproc import xmlproc
from xml.parsers.xmlproc import xmlval
from xml.parsers.xmlproc import xmldtd

def main():
	# Some globals and variables
	global config
	global homedir
	
	config = {}

	options = [
		"--config",
		"--configdump",
		"--daemon",
		"--debug",
		"--verbose",
		"--version"
	]
	shortoptions = {
		"c":"--config",
		"d":"--debug",
		"D":"--daemon",
		"v":"--verbose",
		"V":"--version"
	}
	overwrite = [
		"--daemon",
		"--debug",
		"--verbose"
	]
	

	# Scan for commandline options. This is like the handling 
	# of Gentoo's (http://www.gentoo.org) "emerge". 
	# Thanks vor this inspiration guys!
	
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

	# Some error handling
	if "--daemon" in opts and "--nodaemon" in opts: 
		print "!!! Error: You can not use --daemon and --nodaemon at the same time"
		sys.exit(1)
	
	# "One option, one output and die" (tm)
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
	
	# Get the users application data directory from environment variables and "~/"
	# Try windows path first, as windows has a special application data directory
	# The last fallback is to use the current working directory
	if os.getenv("APPDATA") is not None:
		homedir = os.getenv("APPDATA").replace("\\", "/")
	else:
		homedir = os.path.expanduser("~")
	if not os.path.exists(homedir):
		homedir = os.getenv("HOME")
	if not os.path.exists(homedir):
		homedir = os.getcwd()
		
	# Get the systems global settings directory
	# Try both /etc and the windows "all users" diretory
	if os.path.isdir("/etc/"):
		etcdir = "/etc"
	elif os.getenv("ALLUSERSPROFILE") != "":
		etcdir = os.getenv("ALLUSERSPROFILE").replace("\\", "/") + os.getenv("APPDATA")[len(os.getenv("USERPROFILE")):].replace("\\", "/")
	else:
		etcdir = ""

	if "--config" in opts:
		if opts[opts.index("--config")+1][0:2] == "--":
			print "!!! Error: You specified --config but no file was appended!"
			sys.exit(1)
		config['config'] = opts[opts.index("--config")+1]
	else:
		if os.path.isfile(homedir+"/dirt.xml"):
			config['config'] = homedir+"/dirt.xml"
		elif os.path.isfile(etcdir+"/dirt.xml"):
			config['config'] = etcdir+"/dirt.xml"
		else: 
			print "!!! Error: No configuration file found!"
			sys.exit(1)
		
	# Validate XML
	p = xmlval.XMLValidator()
	p.parse_resource(config['config'])

	configuration = xml.dom.minidom.parse(config['config'])
	
	general_config = configuration.getElementsByTagName('general')
	for node in general_config:
		for general in node.childNodes:
			if general.nodeType == Node.ELEMENT_NODE:
				setname = general.nodeName
			for set in general.childNodes:
				# TODO: We really have to find a nice way to check for bool's. 
				# This is ugly. 
				if string.lower(set.data) == "true":
					config[setname] = True
				elif string.lower(set.data) == "false":
					config[setname] = False
				else:
					config[setname] = set.data
	
	for set in opts:
		if set in overwrite:
			config[set[2:]] = True
	
	# Just give back the whole configuration and exit.
	if "--configdump" in opts:
		pprint.pprint(config)
		sys.exit()

	

if __name__ == "__main__":
	main()
