#!/usr/bin/env python
# OpenBox pipe menu to show currently defined openbox keybindings, and edit them.
#
# modified by aj heller <aj@drfloob.com>, june 2011
# license: GPLv3
# source can be found on github: https://github.com/drfloob/show_ob_keybindings.py
#
# IMPORTANT: you need to change the RCFILE global variable to point to the xml file containing
# your openbox keybindings.
# 
# Also, the default editor is set to emacsclient. If you want to use a different editor you need to
# change the editCommand function below.
#
#
# Original Copyright:
# Copyright 2010 Joe Bloggs (vapniks@yahoo.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from os.path import expanduser
import xml.parsers.expat
from string import strip, replace, rjust
from xml.sax import make_parser
from xml.sax import saxutils
from xml.sax.handler import feature_namespaces

NESTSTR = '--- '
RCFILE = '~/.config/openbox/rc.xml'
CHAIN_KEY_LABEL = 'Chain Key: '
JUSTIFY_SIZE = 100

class rcHandler(saxutils.handler.ContentHandler): # handler class inherits from saxutils.DefaultHandler
    def __init__(self): # constructor 
        self.in_keybind = 0
        self.in_action = 0
        self.in_command = 0
        self.keybind = ''
        self.keybind_string = ''
        self.action = ''
        self.command = ''
        # following line needs to be set to point the xml file containing your openbox keybindings
        self.nesting_level = 0
        
    # this function should return a string containing the command you want to run for the current keybinding        
    def editCommand(self): 
        return 'emacsclient -a emacs -e \'(progn (find-file "' + RCFILE + '") ' + \
            '(goto-char (point-min)) (re-search-forward "\\\"' + self.keybind + '\\\""))\''
        
    # override function from DefaultHandler, called at start of xml element
    def startElement(self, name, attrs): 
        if (name == 'keybind') and (self.in_keybind == 1):
            # chain key has a child! print a tag for it
            self.print_item('separator')

        if name == 'keybind':
            self.nesting_level += 1
            self.in_keybind = 1
            self.keybind = attrs.get('key',None) # Get the keybinding

            # handles the case where the keybind is just a modifier key
            #   usecase: chain key is 'Super_L'
            self.keybind_string = CHAIN_KEY_LABEL
            if (self.keybind == 'Super_L'):
                self.keybind_string += 'Windows'
            elif (self.keybind == 'A'):
                self.keybind_string += 'Alt'
            elif (self.keybind == 'S'):
                self.keybind_string += 'Shift'
            elif (self.keybind == 'C'):
                self.keybind_string += 'Ctrl'
            else:
                self.keybind_string = self.keybind

            # handles the case where a modifier key is used in combination
            self.keybind_string = replace(self.keybind_string,'C-','Ctrl+')
            self.keybind_string = replace(self.keybind_string,'W-','Windows+')
            self.keybind_string = replace(self.keybind_string,'S-','Shift+')
            self.keybind_string = replace(self.keybind_string,'A-','Alt+')
        elif (name == 'action') and (self.in_keybind == 1):
            self.in_action = 1
            self.command = attrs.get('name', None)
        #elif (name == 'command'): #and (self.in_action == 1) and (self.action == 'Execute'):
        #    self.command = ''
        #    self.in_command = 1

    # override function from DefaultHandler, called at end of xml element            
    def endElement(self, name):
        if name == 'keybind':
            self.nesting_level -= 1

            if (self.keybind_string != ''):
                self.print_item()
            else:
                self.print_separator()

            self.in_keybind = 0
            self.in_action = 0
            self.in_command = 0
            self.command = ''
            self.keybind_string = ''

    # override function from DefaultHandler, called as each character outside an xml tag is read
    def characters(self,ch):
        if self.in_command:
            self.command = self.command + ch

    def print_item(self, type='item'):
        label = self.keybind_string 
        if (self.command != ''):
            label = (NESTSTR * self.nesting_level) + label + rjust(strip(self.command), JUSTIFY_SIZE)

        print '<' + type + '  label="' + label + \
                    '">\n<action name="execute"><execute>' + self.editCommand() + '</execute></action>\n</' + type + '>'

    def print_separator(self):
        print '<separator />'

            
if __name__ == '__main__':
    parser = make_parser() # create a parser
    parser.setFeature(feature_namespaces, 0) # tell parser we're not interested in XML namespaces
    dh = rcHandler() # create the document handler
    parser.setContentHandler(dh) # tell the parser to use our document handler
    print '<?xml version="1.0" encoding="UTF-8"?>' # header
    print '<openbox_pipe_menu>' # main pipe menu element
    print '<separator label="Select a keybinding to edit it" />'
    parser.parse(expanduser(RCFILE)) # parse the rc.xml file
    print '</openbox_pipe_menu>\n' # end pipe menu element

