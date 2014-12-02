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
	
	def loadTree(self):
		""" Loads the tree from the filepath specified. If this file is blank or no file is found the user will be asked for another file path"""
		try:
			dataFile = open(self.filePath, 'r')
			lines = dataFile.readlines()
			for line in lines:
				# filters out any lines that are just whitespace
				if not (re.match("^\s*$", line)):
					splitLine = line.split("|",4)
					splitLine = self.removeWhitespace(splitLine[1:4])
					# splits the data into the 3 different fields and removes the whitespace
					self.addEntry(splitLine[0], splitLine[1], splitLine[2])
			# if no information has been saved in the lookup then the file is empty (fires even if full of whitespace)
			if (self.nameLookup == {}):
				raise emptyDatabase
		except IOError  as e:
			# there has been a problem loading the file, request that the user types a new file path
			print "IO Error ({0}): {1}".format(e.errno, e.strerror )
			self.filePath = raw_input("Please enter a new file to load: ")
			loadTree();
		except emptyDatabase as e:
			# the database has not loaded any data therefore request a new file as it appears that this one is blank
			print e.strerror
			self.filePath = raw_input("Please enter a new file to load: ")
			self.loadTree();
		finally:
			# always close the file
			dataFile.close();

	def removeWhitespace(self, inputData):
		"""Removes any excess whitespace from the input, removes trailing and leading whitespace and also removes multiple spacing between words """
		if isinstance(inputData, list):
			# if given a list deal with each individually
			for index in range(len(inputData)):
				inputData[index] = self.removeWhitespace(inputData[index])
		else:
			# remove trailing and leading whitespace fire
			inputData = inputData.upper().strip(' ');
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
				tempEmployee += [newEntry]
				nameLookupUpdate = {name:[tempEmployee]}
				IDLookupUpdate = {employeeID:[treeNode(entryArgs)]}

				# update the lookup tables
				self.idLookup.update(IDLookupUpdate)
				self.nameLookup.update(nameLookupUpdate)
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
			entry = self.nameLookup[employee][0]
			if isinstance(entry, treeNode):
				# if there is just one, then return it
				return self.nameLookup[employee]
			else:
				tempIDList = []
				print "Unfortunately there are multiple entries under " + employee + ". Please type the ID of the employee desired."
				for name in self.nameLookup[employee][0]:
					# print out a list of the employee details to allow the user to check the employee they desire
					tempIDList += [name.getEmployeeID()];
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
			return False;

	def generateString(self, firstEmployee, secondEmployee):
		""" generate the output string """

		# make sure that the input employees are valid inputs
		firstEntry = self.validateEmployee(firstEmployee)
		secondEntry = self.validateEmployee(secondEmployee)

		if (firstEntry == False and secondEntry == False):
			# if both entries are not in the tree ask for both to be re-entered
			firstEmployee = raw_input("Please enter a valid employee name to replace "+ firstEmployee +": ")
			secondEmployee = raw_input("Please enter a valid employee name to replace "+ secondEmployee+": ")
			return self.generateString(firstEmployee, secondEmployee)
		elif (secondEntry == False):
			# if only the second is incorrect then ask for it to be re-entered
			secondEmployee = raw_input("Please enter a valid employee name to replace "+ secondEmployee+": ")
			return self.generateString(firstEmployee, secondEmployee)
		elif (firstEntry == False):
			# if only the first is incorrect then ask for it to be re-entered
			firstEmployee = raw_input("Please enter a valid employee name to replace "+ firstEmployee +": ")
			return self.generateString(firstEmployee, secondEmployee)
		else:
			# initialise the output string
			outputString = ""
			# generate the path to the second node
			secondPath = self.findPath(secondEntry)
			
			# create temporary variables that will change as the string is generated
			employee = firstEntry[0]
			employeeID = employee.getEmployeeID()
			rootDetected = self.commonRootDetection(secondPath, employeeID)

			# if the common root has been detected then stop generating the string 
			while not (rootDetected):
				outputString = outputString+ employee.generateOutputString() + " -> "

				# get the manager
				employeeID = employee.getManagerID()
				rootDetected = self.commonRootDetection(secondPath, employeeID)
				if not rootDetected:
					# as long as the root has not been detected bubble up the tree
					employee = self.idLookup[employeeID][0]
			
			# take note of the manager
			manager = self.idLookup[employeeID][0]
			# remove employee IDs in the second Path that are after the common root
			rootIndex = secondPath.index(employeeID)
			if rootIndex > 0 :
				secondPath = secondPath[:]

				for employeeID in reversed(secondPath):
					# generate the second path string
					employee = self.idLookup[employeeID][0]
					rightString = " <- " + employee.generateOutputString()
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
		while (employee[0].getManagerID() in self.idLookup):
			# while manager ID is still an employee then create the return list
			returnList = returnList + [employee[0].getEmployeeID()]
			employee = self.idLookup[employee[0].getManagerID()];
		# add the highest manager to the return list
		returnList = returnList + [employee[0].getEmployeeID()]
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
print employeeTree.generateString(firstEntry, secondEntry)






