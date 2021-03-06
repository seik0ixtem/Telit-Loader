#AVR SOURCE FILES FOR GSM,SERIAL FUNCTIONALITY###########################
# 	                                                   		#
#                    Copyright (C) 2010  Justin Downs of GRounND LAB	#
#                    www.GroundLab.cc  			1%      	#
#                     							#
#					Code based off:			#
#		      			Josh Levinger  			#
#			http://jlev.media.mit.edu/Projects/GeoTracker 	#
#					Further modified by:		#
#					Lucas Vickars	                #
# This program is free software: you can redistribute it and/or modify 	#
# it under the terms of the GNU General Public License as published by 	#
# the Free Software Foundation, either version 3 of the License, or    	#
# at your option) any later version.                                   	#
#                                                                      	#
# This program is distributed in the hope that it will be useful,      	#
# but WITHOUT ANY WARRANTY; without even the implied warranty of       	#
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        	#
# GNU General Public License for more details.                         	#
#                                                                      	#
# You should have received a copy of the GNU General Public License    	#
# with this program.  If not, see <http://www.gnu.org/licenses/>.      	# 
#########################################################################


import sys,os
import optparse
import setPort
import time
import setWorkingDir #sets working directory to TELITLOADER

global fileInput
global fileLength
global fileName
fileName=None
fileLength=None
fileInput=None

# it is really a problem - without error only scripts of this size uploaded without errors
#MAXFILESIZE=7200
#MAXFILESIZE=32000
CHUNKSIZE=7000
CHUNK_SLEEP_DELAY=10


#Gets file name from options##############################################
def getFile():
	global fileInput
	global fileLength
	global fileName
	parser = optparse.OptionParser()		#create and init optionParser
	parser.add_option("-f", "--file",\
		action = "store", type = "string",\
		dest = "FILE", help="py file name")
	(options, args) = parser.parse_args()		#parse options
	#errorcheck options
	if options.FILE is None:
		print "You must specify a file EG. make upload FILE=myFile.py"
		sys.exit(1) #bad for UNIX
	else:
		fileName = options.FILE						#the name of the file
		absFileName = os.path.abspath(setWorkingDir.codeDir+options.FILE)	#the full path of the file
		print "Opening:"+ absFileName		
		file = open(absFileName,'r')
		fileInput = file.readlines()
		fileLength = os.path.getsize(absFileName)
################to compemnsate for length problems########################
		for line in fileInput:
			pass
			#fileLength += 0 #add 1 onto each line	
##########################################################################
        
	
#Gets file name from options##############################################
def getFileOption():
	global fileInput
	global fileLength
	global fileName
	parser = optparse.OptionParser()		#create and init optionParser
	parser.add_option("-f", "--file",\
		action = "store", type = "string",\
		dest = "FILE", help="py file name")
	(options, args) = parser.parse_args()		#parse options
	#errorcheck options
	if options.FILE is None:
		print "You must specify a file EG. make upload FILE=myFile.py"
		sys.exit(1) #bad for UNIX
	else:
		fileName = options.FILE						#the name of the file
		print "We are acting on: "+ fileName +"\n" 
		return "OK"
##########################################################################


#Sends File###############################################################
def writeFile():
	global fileInput
	global fileLength
	global fileName
	
	print "writing file:"
	print fileName
	print fileLength

	# don't know why this limitation (maybe crucial, don't really know, let's try)
	# ok, big filesize MAY be a problem, but it's solved.
	#  point is that after each chunk we should wait some time to get device to think a bit
	#  or it returns ERROR
	#if int(fileLength)>MAXFILESIZE:
	#	print "#### FILE TOO BIG " + str(MAXFILESIZE)  + " byte max #####"
	#	sys.exit(1)		
	writeCommand= "AT#WSCRIPT=%s,%i\r\n" % (fileName,fileLength)
	print "Sending:" + writeCommand
	setPort.serialOpenCheck()			#open serial connection send AT to check
	setPort.telitPort.flushInput()			#get rid of junk
	setPort.telitPort.write(writeCommand)
	input = setPort.getReply()			#from setPort
	if ">>>" not in input:
		print "didn't get >>>??"
		print input		
		sys.exit(1)
	print"START FILE#########"
	lineMarker=0
	chunk_sent_size=0
	for line in fileInput:
		# + because I don't want to worry if python thinks \n and \r are counted symbols or not
		chunk_sent_size = chunk_sent_size + len(line) + 2
		#print "chunk_sent_size: " + str(chunk_sent_size)
		try:	#two from back is /n/l
			if(line[-1:] == "\r\n"):
				writeLine=line
			#it is somthing else append \r\n
			else:
				writeLine=line#[:-1] + "\r\n"
			#write out to port
			setPort.telitPort.write(writeLine)
			##print what we wrote
			#print "%i: %s" % (lineMarker,writeLine)
			lineMarker+=1
		#	time.sleep(.1) #sleep a bit to see the line
		except setPort.serial.serialutil.SerialTimeoutException:
			print "serial timed out on line " + lineMarker	
			setPort.serialClose()
			sys.exit(1)
		if (chunk_sent_size > CHUNKSIZE):
			time.sleep(CHUNK_SLEEP_DELAY)
			chunk_sent_size = 0
			print "Allow device to digest data for " + str(CHUNK_SLEEP_DELAY) + " sec."
	input = setPort.getReply()
	for line in input:
		if "OK\r\n" in line:
			print "loaded OK"
			break
	else:
		print input
	setPort.telitPort.flush()
	print"END FILE###########"
########################################################################


#DELETE FILES############################################################
def deleteFile():
	global fileLength
	global fileName
	
	setPort.serialOpenCheck()				#open serial connection send AT to check
	deleteCommand= "AT#DSCRIPT=%s\r\n" % (fileName)
	if ".py" in fileName:
		print "\nDELETING .py file:"
		#delete both files .py and .pyo
		print "Sending: " + deleteCommand
		setPort.telitPort.flush()
		setPort.telitPort.write(deleteCommand)
		input = setPort.getReply()
		for lines in input:
			if "OK" in lines:
				print "FOUND AND DELETED:" +fileName
				break	
			elif "ERROR" in lines:
				print "didn't find .py file: " +fileName
				print lines
				break
		#delete .pyo
		print "\nDELETING .pyo file:"
		deleteCommand= "AT#DSCRIPT=%so\r\n" % (fileName) #add 'o' for pyo
		print "Sending: " + deleteCommand
		setPort.telitPort.flushInput()
		setPort.telitPort.write(deleteCommand)
		input = setPort.getReply()
		for lines in input:
			if "OK" in lines:
				print "FOUND AND DELETED:" +fileName+"o"
				break
			elif "ERROR" in lines:
				print "didn't find .pyo file: " +fileName
				print lines
				break
	else:
		print "\nDELETING file:"
		#delete file
		print "Sending: " + deleteCommand
		setPort.telitPort.flush()
		setPort.telitPort.write(deleteCommand)
		input = setPort.getReply()
		for lines in input:
			if "OK" in lines:
				print "FOUND AND DELETED:" +fileName
				break	
			elif "ERROR" in lines:
				print "didn't find .py file: " +fileName
				print lines
				break

	setPort.serialClose()
########################################################################################


#list Files##############################################################################
def listFiles():
	global fileLength
	global fileName
	
	if fileName is None:				#set impossible
		fileName="spoogert"
		fileLength=1000000000
	setPort.serialOpenCheck()			#open serial connection send AT to check
	listCommand= "AT#LSCRIPT\r\n" 
	print "Listing current files:"
	print "Sending: " + listCommand
	setPort.telitPort.flush()
	setPort.telitPort.write(listCommand)
	input = setPort.getReply()
	foundFile="false"
	for line in input:
		print line
		if "#LSCRIPT: \"%s\",%i" % (fileName,fileLength) in line:
			print "*******************************FOUND FILE->" +fileName
			foundFile="true"	
	if foundFile == "true":
		print "#########################################"
		print "FILE: " +fileName + " is stored on Telit.."
		print "#########################################"
	
	setPort.serialClose()
	return input
##########################################################################################

#READ FILE###############################################################################
def readFile():
	global fileName
	setPort.serialOpenCheck()			#open serial connection send AT to check
	readCommand = "AT#RSCRIPT=\"%s\"\r\n" % (fileName)
	print "Reading file: " + fileName
	print "Sending: " + readCommand
	setPort.telitPort.flush()
	setPort.telitPort.write(readCommand)
#	input = setPort.getReply()
	input = setPort.telitPort.readlines()
	#write to log file
	logFile= open("../logFile.txt", 'w')	#overwrite eachtime
	lineMarker=0
	for line in input:
		logFile.write(line)
		time.sleep(.1)
		print "%i: %s"%(lineMarker,line)
		lineMarker+=1
	print "done reading"
	logFile.close()
###########################################################################################

#enableScript##############################################################################
def enableScript():
	global fileName
	setPort.serialOpenCheck()			#open serial connection send AT to check
	if fileName == None:
		readCommand = "AT#ESCRIPT?\r\n" 
	else:
		readCommand = "AT#ESCRIPT=\"%s\"\r\n" % (fileName)
		print "SETTING MAIN() SCRIPT AS: " + fileName
	print "Sending: " + readCommand
	setPort.telitPort.flush()
	setPort.telitPort.write(readCommand)
	input = setPort.getReply()
	print "STATUS:"
	for line in input:
		print line
	setPort.serialClose()
############################################################################################

#deleteAll##################################################################################
def deleteAll():
	global fileName 
	files=listFiles()				#list files get names
	for file in files:		
		if file.find('"') != -1:		#if it has " it has file name
			deleteMe = file.split('"')[1]	#just get file name
			print "FOUND: " + deleteMe	
			fileName = deleteMe		#set global to pass to deleteFile
			deleteFile()			#delete fileName
############################################################################################




#test
######TEST SERIAL
def TESTSERIAL():
	setPort.serialOpenCheck()			#open serial connection send AT to check
	setPort.serialClose()
#################
			
######readFile()
def READFILE():
	getFileOption()
	readFile()
###############

######listAllFiles
def LISTFILE():
	listFiles()
#################

######listLookForFile()
def FINDFILE():
	getFileOption()
	listFiles()
#################

######DELETE FILE
def DELETEFILE():
	getFileOption()
	deleteFile()
################

#####DELETE ALL FILES
def DELETEALL():
	deleteAll()
################

######writeFile()
def WRITEFILE():
	getFile()
	deleteFile()
	writeFile()
################

#####writeCheckfile()
def WRITECHECKFILE():
	getFile()
	writeFile()
	readFile()
###################

####enableScript()##
def ENABLESCRIPT():
	getFileOption()
	enableScript()
###################

####checkEnable##
def CHECKENABLE():
	enableScript()
###################




