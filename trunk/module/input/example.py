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
import syslog

class example(threading.Thread):
	def __init__(self, config):
		self.config = config
		threading.Thread.__init__(self)
	
	def run(self):
		syslog.syslog("Hello World!")

def doc():
	# This is the temporary way to make a documentation
	return "Example INPUT plugin"
