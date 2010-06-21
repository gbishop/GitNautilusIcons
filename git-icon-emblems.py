# -*- coding: utf-8 -*-
# Nautilus GIT Icon Emblems # started life as Nautilus SVN Icon Emblems though very little remains
# Version 1.2
# Copyright (c) 2008, Perberos <perberos@gmail.com>
#                     Gary Bishop <gb@cs.unc.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import urllib
import gtk
import nautilus
from subprocess import Popen, PIPE
import time
import re

parentRE = re.compile(r'[./]+$')

if False:
    fp = file('/tmp/gb.log', 'w')
    import sys
    sys.stdout = sys.stderr = fp
    
    def dbprint(*args):
        if fp:
            fp.write(' '.join([str(arg) for arg in args]))
            fp.write('\n')
            fp.flush()
else:
    def dbprint(*args):
        pass

class GitFolderBranchProvider(nautilus.LocationWidgetProvider):
    '''Display a label in Git controlled folders indicating the branches'''
    def __init__(self):
        pass
    
    def get_widget(self, uri, window):
        filename = urllib.url2pathname(uri[7:])
        p = Popen(["git", "branch"], stdout=PIPE, cwd=filename)
        output = p.communicate()[0]
        if p.returncode != 0:
            dbprint("not git dir")
            return None

        entry = gtk.Label()
        entry.set_text(output.strip())
        entry.show()
        return entry

class GitIconEmblems(nautilus.InfoProvider):
    def __init__(self):
        dbprint("Initializing git-icons-emblems extension")
        # initialize a simple cache
        self.dirname = None
        self.dirtime = time.time()
    
    def update_file_info(self, file):
        # get all values of path and filename
        dbprint('update_file_info')
        
        filename = urllib.url2pathname(file.get_uri()[7:])
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        if file.is_directory():
            basename = basename + '/'
            if os.path.exists(os.path.join(filename, '.git')):
                file.add_emblem('GitOK')
                
        dbprint(filename, dirname, basename)
        
        # cache the output of git status for 10 seconds or until the folder changes
        if self.dirname != dirname or time.time() - self.dirtime > 10:
            self.dirname = dirname
            self.dirtime = time.time()
            self.files = None
            p = Popen(["git", "status", "-s"], stdout=PIPE, cwd=dirname)
            output = p.communicate()[0]
            if p.returncode != 0:
                dbprint("not git dir")
                return
            self.files = {}
            for line in output.split('\n'):
                stat = line[0:2]
                fname = line[3:]
                if parentRE.match(fname) and stat == '??':
                    self.files['..'] = stat
                else:
                    self.files[fname] = stat
                
            dbprint('files=', self.files)
            
        if self.files is None: # not git controlled
            return
            
        stat = self.files.get(basename)
        if stat is None:
            if '..' in self.files:
                file.add_emblem('GitUntracked')
        elif stat == 'A ':
            file.add_emblem('GitAdded') # added
        elif stat == ' M':
            file.add_emblem('GitModified') # modified
        elif stat == 'AM':
            file.add_emblem('GitAdded') # added
            file.add_emblem('GitModified') # modified
        elif stat == '??':
            file.add_emblem('GitUntracked') # untracked
        else:
            file.add_emblem('GitConflict') # conflict or something I didn't account for

