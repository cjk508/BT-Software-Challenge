import sys, re

class emptyDatabase(Exception):
	"""empty Database exception, is raised if there is no data in the file"""
	def __init__(self):
		self.strerror = "The file you have selected appears to be empty"
	def __str__(self):
		return self.strerror

class treeNode(object):
	"""one entry in the tree contains all 3 pieces of information and returns an output string"""
	def __init__(self, arg):
		super(treeNode, self).__init__()
		self.EmployeeID = arg['EmployeeID']
		self.ManagerID = arg['ManagerID']
		self.Name = arg['Name']

	def __str__(self):
		# if printed, print the name of the employee in title case
		return self.Name.title()

	def getName(self):
		return self.Name
	def getEmployeeID(self):
		return self.EmployeeID
	def getManagerID(self):
		return self.ManagerID
	def generateOutputString(self):
		return self.Name.title() +" ("+ self.EmployeeID + ")"

class Tree(object):
	"""Builds and analyses the tree"""
	def __init__(self, arg):
		""" Initialises the tree class, saves the filePath and creates the 2 look up tables. Then it loads the data into the tree"""
		super(Tree, self).__init__()
		self.filePath = arg['filePath']
		self.nameLookup = {}
		self.idLookup = {}
		self.loadTree()
		# removes empty rows that have been created by removed employees
		if '' in self.idLookup:
			del self.idLookup['']
		if '' in  self.nameLookup:
			del self.nameLookup['']
	
	def loadTree(self):
		""" Loads the tree from the filepath specified. If this file is blank or no file is found the user will be asked for another file path"""
		try:
			dataFile = open(self.filePath, 'r')
			lines = dataFile.readlines()
			for line in lines:
				# filters out any lines that are just whitespace
				if not (re.match("^\s*$", line)):
					try:
						splitLine = line.split("|",4)
						splitLine = self.removeWhitespace(splitLine[1:4])
						# splits the data into the 3 different fields and removes the whitespace
						self.addEntry(splitLine[0], splitLine[1], splitLine[2])
					except IndexError as e :
						print "Index Error: attempted to extract data but line was not correctly formatted, this line has been skipped"
			# if no information has been saved in the lookup then the file is empty (fires even if full of whitespace)
			if (self.nameLookup == {}):
				raise emptyDatabase
		except IOError  as e:
			# there has been a problem loading the file, request that the user types a new file path
			print "IO Error ({0}): {1}".format(e.errno, e.strerror )
			self.filePath = raw_input("Please enter a new file to load: ")
			loadTree()
		except emptyDatabase as e:
			# the database has not loaded any data therefore request a new file as it appears that this one is blank
			print e.strerror
			self.filePath = raw_input("Please enter a new file to load: ")
			self.loadTree()
		finally:
			# always close the file
			dataFile.close()

	def removeWhitespace(self, inputData):
		"""Removes any excess whitespace from the input, removes trailing and leading whitespace and also removes multiple spacing between words """
		if isinstance(inputData, list):
			# if given a list deal with each individually
			for index in range(len(inputData)):
				inputData[index] = self.removeWhitespace(inputData[index])
		else:
			# remove trailing and leading whitespace fire
			inputData = inputData.upper().strip(' ')
			# then remove any double (or more) spaces
			inputData = re.sub("\s\s+"," ", inputData)
		return inputData

	def addEntry(self, employeeID, name, managerID ):
		""" Add the data to both look up tables. If there are 2 entries then the lookup will return 2 results """
		# Do not add the field names
		if (employeeID != "EMPLOYEE ID"):
			entryArgs = {
				'Name' : name,
				'ManagerID': managerID,
				'EmployeeID': employeeID
			}
			# create a new tree Node to be added to both lookup tables
			newEntry = treeNode(entryArgs)
			if (name in self.nameLookup):
				# if the entry already exists then add the node to a list so this can be consulted if the input
				# requests this later
				tempEmployee = self.nameLookup[name]
				tempEmployee.append(newEntry)
				nameLookupUpdate = {name:tempEmployee}
				IDLookupUpdate = {employeeID:treeNode(entryArgs)}

				# update the lookup tables
				self.idLookup.update(IDLookupUpdate)
				self.nameLookup.update(nameLookupUpdate)
			elif (employeeID in self.idLookup):
				# skip over duplicates for now, make a list of them as we go through.
				print "Duplicate EmployeeID: {0} not added to tree as Employee ID is a duplicate".format(newEntry.generateOutputString())
			else:
				# if there has not been a duplication then just add node to the tree
				nameLookupUpdate = {name:[treeNode(entryArgs)]}
				IDLookupUpdate = {employeeID:[treeNode(entryArgs)]}
				self.idLookup.update(IDLookupUpdate)
				self.nameLookup.update(nameLookupUpdate)

	def lookupEntry(self, employee):
		""" Checks that the input is in the tree and allows the user to select one if there are multiples, or correct if not in the tree """
		if (employee in self.nameLookup):
			# If the name is in the tree then check this entry for multiples
			entry = self.nameLookup[employee]
			if len(entry) == 1:
				# if there is just one, then return it
				return self.nameLookup[employee]
			else:
				tempIDList = []
				print "Unfortunately there are multiple entries under " + employee + ". Please type the ID of the employee desired."
				for name in self.nameLookup[employee]:
					# print out a list of the employee details to allow the user to check the employee they desire
					tempIDList += [name.getEmployeeID()]
					print "Employee ID: "+name.getEmployeeID()+" | Employee Name: " + name.getName() + " | ManagerID: " + name.getManagerID()
				# allow the user to input their choice 
				chosenID = raw_input("ID of desired Employee: ")
				# validate that the user choice is in the list of possible choices
				while (not chosenID in tempIDList):
					chosenID = raw_input("Sorry "+ chosenID+" is not valid ID for this name. Please enter another ID: ")
				return self.idLookup[chosenID]
		else:
			# returns false if the employee is not in the tree. This can then be dealt with
			print "Unfortunately " +employee+" is not in the database"
			return False

	def createOutput(self, firstEmployee, secondEmployee):
		""" generate the output string """

		# make sure that the input employees are valid inputs
		firstEntry = self.validateEmployee(firstEmployee)
		secondEntry = self.validateEmployee(secondEmployee)

		while (firstEntry == False):
			firstEmployee = raw_input("Please enter a valid employee name to replace "+ firstEmployee +": ")
			firstEntry = self.validateEmployee(firstEmployee)
			if isinstance(firstEntry, list):
				firstEntry = firstEntry[0]
		while (secondEntry == False):
			secondEmployee = raw_input("Please enter a valid employee name to replace "+ secondEmployee+": ")
			secondEntry = self.validateEmployee(secondEmployee)
			if isinstance(secondEntry, list):
				secondEntry = secondEntry[0]

		return self.generateString(firstEntry, secondEntry)
	

	def generateString(self,firstEntry, secondEntry):
		# initialise the output string
		outputString = ""
		# generate the path to the second node
		if isinstance(secondEntry, list):
			secondEntry = secondEntry[0]
		secondPath = self.findPath(secondEntry)
		
		# create temporary variables that will change as the string is generated
		if isinstance(firstEntry, list):
			firstEntry = firstEntry[0]
		employee = firstEntry
		employeeID = employee.getEmployeeID()
		rootDetected = self.commonRootDetection(secondPath, employeeID)


		# if the common root has been detected then stop generating the string 
		while (not rootDetected) and (employeeID != ''):
			outputString = outputString+ employee.generateOutputString() + " -> "

			# get the manager
			employeeID = employee.getManagerID()
			rootDetected = self.commonRootDetection(secondPath, employeeID)
			if (not rootDetected) and (employeeID != ''):
				# as long as the root has not been detected bubble up the tree
				try:
					employee = self.idLookup[employeeID]
					if isinstance(employee, list):
						employee = employee[0]
				except KeyError:
					print "KeyError: could not find the employee entry: \'"+employee.generateOutputString() +"\'"
					return "Output String terminated due to KeyError"
		# take note of the manager
		if (employeeID != ''):
			manager = self.idLookup[employeeID][0]
			# remove employee IDs in the second Path that are after the common root
			rootIndex = secondPath.index(employeeID)
		else:
			manager = employee
			# remove employee IDs in the second Path that are after the common root
			try:
				rootIndex = secondPath.index(manager.getEmployeeID())
			except ValueError:
				print "ValueError: Employee ID is not in the list. Error occurred generating the path from {0}. Employee IDs in this path are {1}.".format(manager.generateOutputString(), secondPath)
				return "Output String terminated due to ValueError"
		if rootIndex > 0 :
			secondPath = secondPath[:rootIndex]
			rightString = ""
			for employeeID in reversed(secondPath):
				# generate the second path string
				try:
					employee = self.idLookup[employeeID]
					if isinstance(employee, list):
						employee = employee[0]
					rightString =rightString + " <- " + employee.generateOutputString()	
				except KeyError:
					print "KeyError: could not find an employee with ID: \'"+employeeID +"\'"
					return "Output String terminated due to KeyError"
			# concatenate the right and left string with the manager in the middle
			return outputString + manager.generateOutputString() + rightString
		else:
			# the root is the furthest right needed
			return outputString + manager.generateOutputString()



	def validateEmployee(self, employee):
		""" normalise and check the initial """
		if not isinstance(employee, treeNode):
			# if employee is a string then normalise it, check that it is in the tree and return the node
			entry = self.removeWhitespace(employee)
			entry = self.lookupEntry(entry)
			return entry
		else:
			# if it is a tree node then this was called unnecessarily
			return employee[0]

	def findPath(self, employee):
		""" Creates the path for the left hand side of the output string by bubbling up through the tree till the root node is found """
		returnList = []
		while (employee.getManagerID() in self.idLookup):
			# while manager ID is still an employee then create the return list
			returnList = returnList + [employee.getEmployeeID()]
			employee = self.idLookup[employee.getManagerID()]
			if isinstance(employee, list):
				employee = employee[0]
		# add the highest manager to the return list
		returnList = returnList + [employee.getEmployeeID()]
		return returnList

	def commonRootDetection(self, secondPath, employeeID):
		""" Detect the employee ID provided is a common root in the path provided"""
		for matchEmployeeID in secondPath:
			if matchEmployeeID == employeeID:
				return True
		# if no matches found return false
		return False

# MAIN EXECUTION

# argument 1 is the path to the python file
if (len(sys.argv) == 1):
	# if there just 1 input then ask for all inputs to be given
	filePath = raw_input("No file path specified, please enter a file path: ")
	firstEntry = raw_input("No employee name\'s were entered, please enter the first employee: ")
	secondEntry = raw_input("No employee name\'s were entered, please enter the second employee: ")
	inputArgs = {
		'filePath' : filePath
	}
elif (len(sys.argv) == 2):
	# if provided with 2 arguments it is assumed that the file path is provided (this assumption will be caught if incorrect and the employee name is not a file name)
	# ask for the employee names to be re-entered 
	firstEntry = raw_input("No employee name\'s were entered, please enter the first employee: ")
	secondEntry = raw_input("No employee name\'s were entered, please enter the second employee: ")
	inputArgs = {
		'filePath' : str(sys.argv[1])
	}
elif (len(sys.argv) == 3):
	# if 3 arguments are provided we are to assume that the 3rd argument is the right most employee to be outputted 
	# ask for the left most employee to be inputted
	firstEntry = str(sys.argv[2])
	secondEntry = raw_input("Only one employee name was entered, please enter the second employee: ")
	inputArgs = {
		'filePath' : str(sys.argv[1])
	}
elif (len(sys.argv) == 4):
	# if 4 arguments are given assume that they are in the correct order. If there is a problem the program will try to rectify it if noticed
	firstEntry = str(sys.argv[2])
	secondEntry = str(sys.argv[3])
	inputArgs = {
		'filePath' : str(sys.argv[1])
	}
# Initialise the tree
employeeTree = Tree(inputArgs)

# print out the output string generated by the tree
outputString =  employeeTree.createOutput(firstEntry, secondEntry)
print "\n\r Output String \n\r"
print outputString





