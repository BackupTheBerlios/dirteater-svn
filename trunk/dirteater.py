#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 
# USA
#
# $Id$

__version__ = "$Rev$"
headurl = "$HeadURL: svn+ssh://svn.berlios.de/svnroot/repos/dirteater/trunk/dirteater.py $"

import os
import sys
import types
import string
import threading
import os.path
import copy
import logging
import pprint
import xml.dom.minidom

from logging import handlers
from xml.dom.minidom import Node
from xml.dom.minidom import Element
from xml.dom.NamedNodeMap import *
from xml.parsers.xmlproc import xmlval, xmlproc
from xml.parsers.xmlproc.utils import ErrorPrinter

from dirtErrHandle import *
from dirtLib import *

def main():
	global config
	
	config = {}
	general_cfg = {}
	plugin_cfg = {}
	
	options = [
		"--config",
		"--configdump",
		"--debug",
		"--daemon",
		"--help",
		"--logtype",
		"--module-help",
		"--nodtd",
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
		"--logtype",
		"--verbose"
	]

	logger = logging.getLogger("dirteater")
	logformat = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
	hdlr = logging.StreamHandler(sys.stdout)
	hdlr.setFormatter(logformat)
	logger.addHandler(hdlr)
	logger.setLevel(logging.WARNING)

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
						logger.info("Redundant use of "+shortoptions[y])
					else:
						cmd.append(shortoptions[y])
				else:
					logger.error(y+" is an invalid shortoption!")
					sys.exit(1)
		else:
			cmd.append(x)
	for x in cmd:
		if len(x) >= 2 and x[0:2] == "--":
			if x in opts:
				logger.info("Redundant use of "+x)
			if x in options:
				opts.append(x)
			else:
				logger.error(x+" is an invalid option!")
				sys.exit(1)
		else:
			opts.append(x)
	
	if "--help" in opts: 
		print "This is dirteater (http://dirteater.berlios.de). The information management system.\n"""
		print "These are the availibale command line options:\n"
		print "--config <path>\t\t Specify configuration file manually"
		print "--configdump \t\t Parse configuation file and print out all configuration variables"
		print "--daemon \t\t Make dirteater daemonic"
		print "--debug \t\t Debugging output"
		print "--help \t\t\t Display this help message"
		print "--logtype \t\t Where do you want to log? See manual page for more information"
		print "--module-help <module> \t Display help for a module and exit. Modules are named for example: 'output:hello'"
		print "--nodtd \t\t Make no validation against a DTD"
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
			print __version__
		sys.exit()
	elif "--module-help" in opts:
		if len(opts) < 2:
			logger.error("You want to use --module-help, but no module was appended!")
			sys.exit(1)
		elif opts[opts.index("--module-help")+1][0:2] == "--" or len(opts) <= 1:
			logger.error("You want to use --module-help, but no module was appended!")
			sys.exit(1)
		else:
			moduleinfo = string.split(opts[opts.index("--module-help")+1], ":")
			if len(moduleinfo) < 1:
				logger.error("You have to specify the module you want help for in this syntax 'output:hello'")
				sys.exit(1)
			else: 
				if moduleinfo[0] != "output" and moduleinfo[0] != "input":
					print moduleinfo[0]
					logger.error("You have specified a wrong module type. You only can use 'input' or 'output'")
					sys.exit(1)
				else: 
					print "Help for "+moduleinfo[0]+" module '"+moduleinfo[1]+"':\n"
					modulename = "module."+str(moduleinfo[0])+"."+str(moduleinfo[1])
					exec "import "+modulename
					print eval(modulename+".doc()")
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
		
	if os.path.isdir("/etc/"):
		etcdir = "/etc"
	elif os.getenv("ALLUSERSPROFILE") != "":
		etcdir = os.getenv("ALLUSERSPROFILE").replace("\\", "/") + os.getenv("APPDATA")[len(os.getenv("USERPROFILE")):].replace("\\", "/")
	else:
		etcdir = ""

	if "--config" in opts:
		if len(opts) == 1:
			logger.error("You want to use --config, but no file was appended!")
			sys.exit(1)
		elif opts[opts.index("--config")+1][0:2] == "--" or len(opts) <= 1:
			logger.error("You want to use --config, but no file was appended!")
			sys.exit(1)

		if os.path.isfile(opts[opts.index("--config")+1]) is False:
			logger.error("Configuration file not found!")
			sys.exit()
		else:
			general_cfg[u'config'] = opts[opts.index("--config")+1]
	else:
		if os.path.isfile(homedir+"/.dirt.xml"):
			general_cfg[u'config'] = homedir+"/.dirt.xml"
		elif os.path.isfile(etcdir+"/dirt.xml"):
			general_cfg[u'config'] = etcdir+"/dirt.xml"
		else: 
			logger.error("No configuration file can be found!")
			sys.exit()
	
	if "--nodtd" in opts: 
		logger.warning("--nodtd is appended. Now no validation against a DTD is made! Only do this for debugging or testing of new features!")
	else:
		try: 
			parser = xmlval.XMLValidator()
			parser.set_error_handler(dtdErrHandle(parser))
			parser.parse_resource(config['config'])
		except Exception, msg:
			print msg
			sys.exit()

	configuration = xml.dom.minidom.parse(general_cfg['config'])

	subnode_cfg = {}
	
	generalconfig = configuration.getElementsByTagName('general')
	for mainnode in generalconfig: 
		for subnode in mainnode.childNodes:
			if subnode.nodeType == Node.ELEMENT_NODE:
				for lastnode in subnode.childNodes:
					if lastnode.nodeType == Node.ELEMENT_NODE:
						general_cfg[lastnode.parentNode.nodeName] = subnode_cfg
						for content in lastnode.childNodes:
							subnode_cfg[lastnode.nodeName] = xmlVarConvert(content.data)
					elif lastnode.nodeType == Node.TEXT_NODE:
						if len(string.strip(lastnode.data)) > 0:
							general_cfg[lastnode.parentNode.nodeName] = xmlVarConvert(lastnode.data)
				subnode_cfg = {}

	pluginconfig = configuration.getElementsByTagName('plugin')
	for mainnode in pluginconfig: 
		for subnode in mainnode.childNodes:
			if subnode.nodeType == Node.ELEMENT_NODE:
				pluginname = mainnode.getAttribute("name")
				plugintype = mainnode.getAttribute("type")
				pluginenable = mainnode.getAttribute("enable")

				for lastnode in subnode.childNodes:
					if len(string.strip(lastnode.data)) > 0:
						subnode_cfg[subnode.nodeName] = lastnode.data

		plugin_cfg[pluginname] = subnode_cfg
		subnode_cfg = {}

	config['general'] = general_cfg
	config['plugin'] = plugin_cfg

	# this is a crazy logging system. but is it secure?
	log = {
		"stdout":{"class":"StreamHandler","opts":""},
		"file":{"class":"FileHandler", "opts":"'"+config['general']['logging']['file']+"'"},
		"rotating-file":{"class":"handlers.RotatingFileHandler", \
			"opts":"'"+config['general']['logging']['file'] \
			+"', maxBytes='"+config['general']['logging']['size'] \
			+"', backupCount='"+config['general']['logging']['count']+"'"},
		"windowslog":{"class":"NTEventLogHandler", "opts":"'dirteater', logtype='Application'"},
		"syslog":{"class":"handlers.SysLogHandler","opts":""}
	}

	logger.removeHandler(hdlr)
	exec "user_hdlr = logging." \
		+log[config['general']['logging']['type']]['class'] \
		+"("+log[config['general']['logging']['type']]["opts"]+")"
	user_hdlr.setFormatter(logformat)
	logger.addHandler(user_hdlr)

	if config['general']['logging']['debug'] is True: 
		logger.setLevel(logging.DEBUG)
	elif config['general']['logging']['verbose'] is True:
		logger.setLevel(logging.INFO)

	if "--configdump" in opts:
		print "This is your configuration:\n"
		pprint.pprint(config)
		sys.exit()

if __name__ == "__main__":
	main()
