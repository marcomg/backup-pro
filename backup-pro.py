#!/usr/bin/python3

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
########################################################################

import argparse
from libbackuppro import BackupPro
import libitunitsconversion

# Setting arguments
argparse = argparse.ArgumentParser(prog='backup-pro', description='A program to generate backups')
argparse.add_argument('--version', action='version', version='%(prog)s version 1.0.0')
argparse.add_argument('patch', action='store', type=str, help='patch to backup')
argparse.add_argument('--olddatabase', '-d', action='store', help='old database patch to make an incremental bakcup')
argparse.add_argument('--split', '-s', action='store', help='in how many bytes split the backup? You can use the suffix MB and GB. Insert CD or DVD of 700MB or 4.7GB')
#argparse.add_argument('--buildiso', '-b', action='store_true', help='if the software have to build the iso to burn backups on CDs or DVDs')
args = argparse.parse_args()


# Start backup
bp = BackupPro(str(args.patch))

# Get all files
files = bp.getFiles()

# Get all sums
sums = bp.getSums(files)

# If is isset and old database remove the files which have the same name and sums:
if(args.olddatabase != None):
    olddb = bp.dbparse(args.olddatabase)
    #commonFiles = bp.getFilesInTwoListsAndSums(files, sums, olddb[0], olddb[1])
    toBackupFiles = bp.getFilesEditedAndSums(files, sums, olddb[0], olddb[1])
    removedFiles = bp.deleteFilesOfThePreviousBackup(files, sums, olddb[0], olddb[1])
    deleteScript = bp.generateDeleteScript(removedFiles)
else:
    toBackupFiles = files

# Generate a new database of files and md5
database = bp.dbgenerator(files, sums)

# Set if split files
if args.split == None:
    split = False
    supportSize = 0
else:
    split = True
    supportSize = str(args.split)
    supportSize = libitunitsconversion.getBytes(supportSize)

# Get the patches of files
newFiles, oldfiles = bp.getWhereCopyFiles(toBackupFiles, split, supportSize)

# Copy the files
bp.copy(oldfiles, newFiles)

# Create the delete script
if(args.olddatabase != None):
    ds = open(bp.destinationPrefix + '1/deleteScript.sh', 'w')
    ds.write(deleteScript)
    ds.close()

# Write the database
databaseF = open(bp.destinationPrefix + '1/database.md5', 'w')
databaseF.write(database)
databaseF.close()

# Build the iso
#if args.buildiso:
#    bp.makeIso();