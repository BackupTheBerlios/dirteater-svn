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
#
# $Id$

__version__ = "$Rev$"

"""
This is a sample module. 

At least you need the methods / functions:
	- __init__
	- run
	- doc
"""

import threading
import sys
import string
import logging
import os
import os.path

class fifo(threading.Thread):
	def __init__(self, config, logger):
		self.config = config
		self.logger = logger
		
		threading.Thread.__init__(self)
	
	def run(self):
		if os.name == "posix": 
			if not os.path.exists(self.config['plugin'][self.__class__.__name__[:]]['fifo']):
				self.logger.debug("Making FIFO ("+self.config['plugin'][self.__class__.__name__[:]]['fifo']+")")
				os.mkfifo(self.config['plugin'][self.__class__.__name__[:]]['fifo'])
			else: 
				self.logger.debug("FIFO already exists ("+self.config['plugin'][self.__class__.__name__[:]]['fifo']+")")
	
			self.logger.debug("Waiting for input to FIFO")
			f = open(self.config['plugin'][self.__class__.__name__[:]]['fifo'], "r")
			for content in f.readlines():
				print content
		else: 
			self.logger.error("This plugin is only for POSIX style operating systems. Disabling plugin")
			return 0


def doc():
	# This is the temporary way to make a documentation
	return "This module make's a FIFO file where you can pipe your informations in."
