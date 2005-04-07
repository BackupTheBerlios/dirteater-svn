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

__version__ = "$Id$"

"""
	This is a sample module. 
	You can do nearly everything what you want with them :)

	At least you need the methods:
		- __init__ 
		- returnFiltered
"""

class imap:						# The classname MUST be the name of the module
	def __init__(conf):
		# here you should become your configuration
		# do what you want with them :)
		return 0

	def getDirt():
		# Get the dirt
		return 0

	def doScore():
		# Make scoring
		return 0

	def returnFiltered
		# Return the filtered messages 
		return 0


def doc():
	# This is the temporary way to make a documentation
	return "Example INPUT plugin"
