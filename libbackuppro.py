#!/usr/bin/python3

import hashlib
import os
import os.path
import shutil
import libitunitsconversion

# Generate a correct patch
def perfectPatch(patch):
    patch = str(patch)
    if(patch[-1] == '/'):
        pass
    else:
        patch = patch + '/';

    if(patch[0] == '/'):
        pass
    else:
        patch = '/' + patch;
    return patch

# Get recoursivly a file list
def getRecoursiveFileList(root):
    fileList = []
    for path, subdirs, files in os.walk(root):
        for file in files:
            fileList.append(os.path.join(path, file))
    return fileList

# Get a listo of sizes from a list of files
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

# From two patches get the difference, for exaple: print(patchDiff('/home/utente/cartella/altracartella/file', '/home/utente/cartella/')) returns: 'altracartella/file'
def patchDiff(original, partial):
    leng = len(partial)
    leng -= 1;
    output = original[leng:]
    return output

# Create direcoties of a patch
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
class backuppro():
    # Save the patch of the dir to backup
    def __init__(self, patch):
        self.backupPatch = patch
    
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
        # If I have to split the files
        if split:
            supportSize = libitunitsconversion.getBytes(supportSize)
            sizes = getFileSizeList(files)
            finalReturn = []
            i = 0
            while(files != []):
                i += 1
                tmpRSize = 0 # Dimensione del gruppo temporaneo
                tmpList = [] # Lista temporanea
                secondWhile = 1 # Valore dei tentativi di partenza
                whileSize = 0 # Dimensione dei dati durante il while (se il for non aggiunge niente viene interrotto)
                # Scorro la lista
                while(secondWhile <= 2): # Se il for qui sotto non fa nulla cambio gruppo
                    # Controllo che il for lavori, se non lavora aumento i tentetivi per far interrompere il ciclo
                    if(whileSize == tmpRSize):
                        secondWhile += 1
                    else:
                        whileSize = tmpRSize
                    
                    # Scorro i file da aggiungere
                    for tmpFile in files:
                        idx = files.index(tmpFile)
                        tmpSize = sizes[idx]
                        # se i files entrano nel disco li aggiungo, altrimenti finisco il disco
                        if((tmpRSize + tmpSize) <= supportSize):
                            tmpRSize += tmpSize# Aggiorno la dimensione
                            tmpList.append(files[idx])# aggiungo il percorso ad una lista temporanea
                            
                            # rimuovo gli item dalla lista
                            del files[idx]
                            del sizes[idx]
                
                # se la lista temporanea è vuota non riesco ad inserire i files nel range
                if(tmpList == []):
                    print('Error some files are too big:')
                    print(files)
                    exit()
                # se non è vuota posso procedere a salvare i dati
                else:
                    for tfile in tmpList:
                        finalReturn.append(str(i) + patchDiff(tfile, self.backupPatch))
            return(finalReturn)
        # If I haven't to split the files
        else:
            rfiles = []
            for myfile in files:
                # original patch, 
                rfiles.append(str(1) + patchDiff(myfile, self.backupPatch))
            return rfiles
    
    # Copy a list of files to a list of destinations
    def copy(self, orig, dest):
        i = 0;
        while (i+1) <= len(orig):
            fileMakedirs(dest[i])
            superCopyFile(orig[i], dest[i])
            i += 1
    
    def makeIso(self):
        pass
    
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