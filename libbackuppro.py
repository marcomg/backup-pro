########################################################################
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.#
#                                                                      #
# Copyright (C) 2014 by Marco Guerrini                                 #
# Version: 1.0.0                                                       #
########################################################################

import hashlib
import os
import shutil

# Generate a correct patch
def perfectPatch(patch):
    patch = str(patch)
    if(patch[-1] != '/'):
        patch += '/';
    return patch

# Get recursively a file list
def getRecoursiveFileList(root):
    fileList = []
    for path, subdirs, files in os.walk(root):
        for file in files:
            fileList.append(os.path.join(path, file))
    return fileList

# Get a list of sizes from a list of files
def getFileSizeList(lfiles):
    size = []
    for vfile in lfiles:
        size.append(os.path.getsize(vfile))
    return size

# Generate an md5 checksum of a file
def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

# From two patches get the difference, for example: print(patchDiff('/home/utente/cartella/altracartella/file', '/home/utente/cartella/')) returns: 'altracartella/file'
def patchDiff(original, partial):
    leng = len(partial)
    output = original[leng:]
    return output

# Create directories of a patch
def makedirs(patch):
    patch = os.path.realpath(patch)
    if os.path.exists(patch):
        pass
    else:
        os.makedirs(patch)

# Create directories for a file
def fileMakedirs(cfile):
    cfile = os.path.dirname(cfile)
    makedirs(cfile)

# Copy a file from source to output and create the directories if they doeesn't exist
def superCopyFile(source, output):
    makedirs(source)
    shutil.copy(source, output)

# Class to make backups
class BackupPro():
    # Save the patch of the dir to backup
    def __init__(self, patch):
        self.backupPatch = patch
        self.destinationPrefix = 'disk_' # il prefisso della destinazione dei files: disk_1, disk_2, etc
        self.destinationSubdir = '/backup' # la sottocartella dove salvare il backup. La forma deve essere /sottocartella e non diversamente!
    
    # Get the file list
    def getFiles(self):
        patch = perfectPatch(self.backupPatch)
        files = getRecoursiveFileList(patch)
        return(files)
    
    # Get the sums from a file list
    def getSums(self, files):
        sums = []
        for myfile in files:
            sums.append(md5Checksum(myfile))
        return sums
    
    # Parse the database and return a list with two list: the list of the files and the list of the sums of theese files
    def dbparse(self, patch):
        db = open(patch, 'r')
        dbcontentlines = db.readlines()
        db.close()
        
        patches = [];
        sums = [];
        
        for dbline in dbcontentlines:
            line = dbline.split("\t", 1)
            patches.append(line[0]);
            sums.append(line[1][:-1])
        return [patches, sums]
    
    # Generate the database of the files: patch(\t)sum(\n)
    def dbgenerator(self, patches, sums):
        i=0
        dbcontent = ''
        while (i+1) <= len(sums):
            dbcontent += patches[i] + "\t" + sums[i] + "\n"
            i += 1
        return dbcontent
    
    # Get the new name from the old name separated by the support size, return a list
    def getWhereCopyFiles(self, ifiles, split = False, supportSize = 0):
        files = ifiles[:]
        sizes = getFileSizeList(files)
        finalDest = []
        finalOrig = []
        i = 0
        if split:
            while(1):
                i += 1
                whileTmp = []
                whileSize = 0
                for j in [0, 1, 2, 3]:
                    for file in files:
                        idx = files.index(file)
                        if (whileSize + sizes[idx]) <= supportSize:
                            whileTmp.append(file)
                            whileSize += sizes[idx]
                            del files[idx]
                            del sizes[idx]
                if whileTmp == []:
                    print('Some files are too big:')
                    for file in files:
                        print(' * %s' % (file))
                    exit()
                elif files == []:
                    break
                else:
                    for file in whileTmp:
                        finalDest.append(self.destinationPrefix + str(i) + self.destinationSubdir + '/' + patchDiff(file, self.backupPatch))
                        finalOrig.append(file)
            return([finalDest, finalOrig])
        else:
            finalDest = []
            finalOrig = []
            for file in files:
                finalDest.append(self.destinationPrefix + str(1) + self.destinationSubdir + '/' + patchDiff(file, self.backupPatch))
                finalOrig.append(file)
            return([finalDest, finalOrig])
    
    # Copy a list of files to a list of destinations
    def copy(self, orig, dest):
        i = 0;
        while (i+1) <= len(orig):
            fileMakedirs(dest[i])
            superCopyFile(orig[i], dest[i])
            i += 1
    
    # Get the files which are in two lists (common files)
    def getFilesInTwoListsAndSums(self, files, sums, oldfiles, oldsums):
        # Get files in two lists:
        i = 0;
        doublefiles = []
        doublesums = []
        
        while (i+1) <= len(files):
            j = 0
            while (j+1) <= len(oldfiles):
                # If the file has the same name of the old file and the same sum I copy it
                if (files[i] == oldfiles[j]) and (sums[i] == oldsums[j]):
                    doublefiles.append(files[i]) # Files in two lists
                    doublesums.append(sums[i]) # Sum of that files
                j += 1
            i += 1
        return doublefiles
    
    # Get different files (new or edited files)
    def getFilesEditedAndSums(self, files, sums, oldfiles, oldsums):
        # Get files in two lists:
        i = 0
        doublefiles = []
        doublesums = []
        
        # Get edited files
        while (i+1) <= len(files):
            j = 0
            while (j+1) <= len(oldfiles):
                # If the file has the same name of the old file and a different sum I copy it
                if (files[i] == oldfiles[j]) and (sums[i] != oldsums[j]):
                    doublefiles.append(files[i]) # Files in two lists
                    doublesums.append(sums[i]) # Sum of that files
                j += 1
            i += 1
        # Get new files:
        for tmp in files:
            if tmp not in oldfiles:
                doublefiles.append(tmp)
        return doublefiles
    
    # Deleted files
    def deleteFilesOfThePreviousBackup(self, files, sums, oldfiles, oldsums):
        deletedfiles = []
        for tmp in oldfiles:
            if tmp not in files:
                deletedfiles.append(tmp)
        return(deletedfiles)
    
    # Create a bash script to delete files are in the old backup, but not in the new
    def generateDeleteScript(self, files):
        script = '#!/bin/bash' + "\n"
        for tmpfile in files:
            script += "rm -f '" + tmpfile + "'" + ';' + "\n"
        return script