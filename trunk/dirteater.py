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
import traceback
import pprint
import xml.dom.minidom

from errHandle import *

from xml.dom.minidom import Node
from xml.dom.minidom import Element
from xml.parsers.xmlproc import xmlval, xmlproc
from xml.parsers.xmlproc.utils import ErrorPrinter

def main():
	# Some globals and variables
	global config
	global homedir
	
	config = {}

	options = [
		"--config",
		"--configdump",
		"--debug",
		"--daemon",
		"--help",
		"--module-help",
		"--verbose",
		"--version"
	]
	shortoptions = {
		"c":"--config",
		"d":"--debug",
		"D":"--daemon",
		"h":"--help",
		"H":"--module-help",
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
					print "!!! Error: -"+y+" is an invalid shortoption."
					sys.exit(1)
		else:
			cmd.append(x)
	for x in cmd:
		if len(x) >= 2 and x[0:2] == "--":
			if x in options:
				opts.append(x)
			else:
				print "!!! Error "+x+" is an invalid option."
				sys.exit(1)
		else:
			opts.append(x)
	
	# "One option, one output and die" (tm)
	if "--help" in opts: 
		print "This is dirteater (http://dirteater.berlios.de). The information management system.\n"
		print "These are the availibale command line options:\n"
		print "--config <path>\t\t Specify configuration file manually"
		print "--configdump \t\t Parse configuation file and print out all configuration variables"
		print "--daemon \t\t Make dirteater daemonic"
		print "--debug \t\t Degging output"
		print "--help \t\t\t Display this help message"
		print "--module-help <module> \t Display help for a module and exit. Modules are named for example: 'output:hello'"
		print "--verbose \t\t Make output verbose"
		print "--version \t\t Print out version information and exit\n"
		print "Please report bugs to <dirteater-dev@lists.berlios.de>\n"
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
	elif "--module-help" in opts:
		if len(opts) < 2:
			print "!!! Error: You want to use --module-help, but no module was appended!"
			sys.exit(1)
		elif opts[opts.index("--module-help")+1][0:2] == "--" or len(opts) <= 1:
			print "!!! Error: You want to use --module-help, but no module was appended!"
			sys.exit(1)
		else:
			moduleinfo = string.split(opts[opts.index("--module-help")+1], ":")
			if len(moduleinfo) < 1:
				print "!!! Error: You have to specify the module you want help for in this syntax 'output:hello'"
				sys.exit(1)
			else: 
				if moduleinfo[0] != "output" and moduleinfo[0] != "input":
					print moduleinfo[0]
					print "!!! Error: You have specified a wrong module type. You only can use 'input' or 'output'"
					sys.exit(1)
				else: 
					print "Help for "+moduleinfo[0]+" module '"+moduleinfo[1]+"':"
					# We should do an import like this: 
					#import modules.moduleinfo[0].moduleinfo[1]
					# 
					# probably this works with the module "imp"
					print "\n\t this feature is not implemented yet \t\n"
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
		if len(opts) == 1:
			print "!!! Error: You want to use --config, but no file was appended!"
			sys.exit(1)
		elif opts[opts.index("--config")+1][0:2] == "--" or len(opts) <= 1:
			print "!!! Error: You want to use --config, but no file was appended!"
			sys.exit(1)
		config['config'] = opts[opts.index("--config")+1]
	else:
		if os.path.isfile(homedir+"/.dirt.xml"):
			config['config'] = homedir+"/.dirt.xml"
		elif os.path.isfile(etcdir+"/dirt.xml"):
			config['config'] = etcdir+"/dirt.xml"
		else: 
			print "!!! Error: No configuration file found!"
			sys.exit(1)
		
	# Validate XML
	try: 
		parser = xmlval.XMLValidator()
		parser.set_error_handler(dtdErrHandle(parser))
		parser.parse_resource(config['config'])
	except Exception, msg:
		print msg
		sys.exit()

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
