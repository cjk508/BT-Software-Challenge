import sys, re


class EmptyDatabase(Exception):
	"""empty Database exception, is raised if there is no data in the file"""

	def __init__(self):
		self.strerror = "The file you have selected appears to be empty"

	def __str__(self):
		return self.strerror


class TreeNode(object):
	"""one entry in the tree contains all 3 pieces of information and returns an output string"""

	def __init__(self, arg):
		super(TreeNode, self).__init__()
		self.employee_id = arg['employee_id']
		self.manager_id = arg['manager_id']
		self.name = arg['name']

	def __str__(self):
		# if printed, print the name of the employee in title case
		return self.name.title()

	def get_name(self):
		return self.name

	def get_employee_id(self):
		return self.employee_id

	def get_manager_id(self):
		return self.manager_id

	def generate_output_string(self):
		return self.name.title() + " (" + self.employee_id + ")"


def common_root_detection(second_path, employee_id):
	""" Detect the employee ID provided is a common root in the path provided"""
	for match_employee_id in second_path:
		if match_employee_id == employee_id:
			return True
	# if no matches found return false
	return False


class Tree(object):
	"""Builds and analyses the tree"""

	def __init__(self, arg):
		""" Initialises the tree class, saves the filePath and creates the 2 look up tables. Then it loads the data
		into the tree """
		super(Tree, self).__init__()
		self.file_path = arg['filePath']
		self.name_lookup = {}
		self.id_lookup = {}
		self.load_tree()
		# removes empty rows that have been created by removed employees
		if '' in self.id_lookup:
			del self.id_lookup['']
		if '' in self.name_lookup:
			del self.name_lookup['']

	def load_tree(self):
		""" Loads the tree from the filepath specified. If this file is blank or no file is found the user will be
		asked for another file path """
		global data_file
		try:
			data_file = open(self.file_path, 'r')
			lines = data_file.readlines()
			for line in lines:
				# filters out any lines that are just whitespace
				if not (re.match("^\s*$", line)):
					try:
						split_line = line.split("|", 4)
						split_line = self.remove_whitespace(split_line[1:4])
						# splits the data into the 3 different fields and removes the whitespace
						self.add_entry(split_line[0], split_line[1], split_line[2])
					except IndexError as e:
						print(
							"Index Error: attempted to extract data but line was not correctly formatted, this line has been skipped")
			# if no information has been saved in the lookup then the file is empty (fires even if full of whitespace)
			if self.name_lookup == {}:
				raise EmptyDatabase
		except IOError  as e:
			# there has been a problem loading the file, request that the user types a new file path
			print("IO Error ({0}): {1}".format(e.errno, e.strerror))
			self.file_path = raw_input("Please enter a new file to load: ")
			self.load_tree()
		except EmptyDatabase as e:
			# the database has not loaded any data therefore request a new file as it appears that this one is blank
			print(e.strerror)
			self.file_path = raw_input("Please enter a new file to load: ")
			self.load_tree()
		finally:
			# always close the file
			data_file.close()

	def remove_whitespace(self, input_data):
		"""Removes any excess whitespace from the input, removes trailing and leading whitespace and also removes
		multiple spacing between words """
		if isinstance(input_data, list):
			# if given a list deal with each individually
			for index in range(len(input_data)):
				input_data[index] = self.remove_whitespace(input_data[index])
		else:
			# remove trailing and leading whitespace fire
			input_data = input_data.upper().strip(' ')
			# then remove any double (or more) spaces
			input_data = re.sub("\s\s+", " ", input_data)
		return input_data

	def add_entry(self, employee_id, name, manager_id):
		""" Add the data to both look up tables. If there are 2 entries then the lookup will return 2 results """
		# Do not add the field names
		if (employee_id != "EMPLOYEE ID"):
			entry_args = {
				'name': name,
				'manager_id': manager_id,
				'employee_id': employee_id
			}
			# create a new tree Node to be added to both lookup tables
			new_entry = TreeNode(entry_args)
			if (name in self.name_lookup):
				# if the entry already exists then add the node to a list so this can be consulted if the input
				# requests this later
				temp_employee = self.name_lookup[name]
				temp_employee.append(new_entry)
				name_lookup_update = {name: temp_employee}
				id_lookup_update = {employee_id: TreeNode(entry_args)}

				# update the lookup tables
				self.id_lookup.update(id_lookup_update)
				self.name_lookup.update(name_lookup_update)
			elif employee_id in self.id_lookup:
				# skip over duplicates for now, make a list of them as we go through.
				print("Duplicate EmployeeID: {0} not added to tree as Employee ID is a duplicate".format(
					new_entry.generate_output_string()))
			else:
				# if there has not been a duplication then just add node to the tree
				name_lookup_update = {name: [TreeNode(entry_args)]}
				id_lookup_update = {employee_id: [TreeNode(entry_args)]}
				self.id_lookup.update(id_lookup_update)
				self.name_lookup.update(name_lookup_update)

	def lookup_entry(self, employee):
		""" Checks that the input is in the tree and allows the user to select one if there are multiples, or correct if not in the tree """
		if (employee in self.name_lookup):
			# If the name is in the tree then check this entry for multiples
			entry = self.name_lookup[employee]
			if len(entry) == 1:
				# if there is just one, then return it
				return self.name_lookup[employee]
			else:
				temp_id_list = []
				print(
					"Unfortunately there are multiple entries under " + employee + ". Please type the ID of the employee desired.")
				for name in self.name_lookup[employee]:
					# print out a list of the employee details to allow the user to check the employee they desire
					temp_id_list += [name.get_employee_id()]
					print(
						"Employee ID: " + name.get_employee_id() + " | Employee Name: " + name.get_name() + " | ManagerID: " + name.get_manager_id())
				# allow the user to input their choice
				chosen_id = raw_input("ID of desired Employee: ")
				# validate that the user choice is in the list of possible choices
				while not chosen_id in temp_id_list:
					chosen_id = raw_input(
						"Sorry " + chosen_id + " is not valid ID for this name. Please enter another ID: ")
				return self.id_lookup[chosen_id]
		else:
			# returns false if the employee is not in the tree. This can then be dealt with
			print("Unfortunately " + employee + " is not in the database")
			return False

	def create_output(self, first_employee, second_employee):
		""" generate the output string """

		# make sure that the input employees are valid inputs
		first_entry = self.validate_employee(first_employee)
		second_entry = self.validate_employee(second_employee)

		while first_entry == False:
			first_employee = raw_input("Please enter a valid employee name to replace " + first_employee + ": ")
			first_entry = self.validate_employee(first_employee)
			if isinstance(first_entry, list):
				first_entry = first_entry[0]
		while (second_entry == False):
			second_employee = raw_input("Please enter a valid employee name to replace " + second_employee + ": ")
			second_entry = self.validate_employee(second_employee)
			if isinstance(second_entry, list):
				second_entry = second_entry[0]

		return self.generate_string(first_entry, second_entry)

	def generate_string(self, first_entry, second_entry):
		# initialise the output string
		output_string = ""
		# generate the path to the second node
		if isinstance(second_entry, list):
			second_entry = second_entry[0]
		second_path = self.find_path(second_entry)

		# create temporary variables that will change as the string is generated
		if isinstance(first_entry, list):
			first_entry = first_entry[0]
		employee = first_entry
		employee_id = employee.get_employee_id()
		root_detected = common_root_detection(second_path, employee_id)

		# if the common root has been detected then stop generating the string
		return self.detect_common_root(employee, employee_id, output_string, root_detected, second_path)

	def detect_common_root(self, employee, employee_id, output_string, root_detected, second_path):
		while (not root_detected) and (employee_id != ''):
			output_string = output_string + employee.generate_output_string() + " -> "

			# get the manager
			employee_id = employee.get_manager_id()
			root_detected = common_root_detection(second_path, employee_id)
			if (not root_detected) and (employee_id != ''):
				# as long as the root has not been detected bubble up the tree
				try:
					employee = self.id_lookup[employee_id]
					if isinstance(employee, list):
						employee = employee[0]
				except KeyError:
					print("KeyError: could not find the employee entry: \'" + employee.generateOutputString() + "\'")
					return "Output String terminated due to KeyError"
		# take note of the manager
		if employee_id != '':
			manager = self.id_lookup[employee_id][0]
			# remove employee IDs in the second Path that are after the common root
			root_index = second_path.index(employee_id)
		else:
			manager = employee
			# remove employee IDs in the second Path that are after the common root
			try:
				root_index = second_path.index(manager.get_employee_id())
			except ValueError:
				print("ValueError: Employee ID is not in the list. Error occurred generating the path from {0}. " \
					  "Employee IDs in this path are {1}.".format(
					manager.generate_output_string(), second_path))
				return "Output String terminated due to ValueError"
		return self.output_root(manager, output_string, root_index, second_path)

	def output_root(self, manager, output_string, root_index, second_path):
		if root_index > 0:
			second_path = second_path[:root_index]
			right_string = ""
			for employee_id in reversed(second_path):
				# generate the second path string
				try:
					employee = self.id_lookup[employee_id]
					if isinstance(employee, list):
						employee = employee[0]
					right_string = right_string + " <- " + employee.generate_output_string()
				except KeyError:
					print("KeyError: could not find an employee with ID: \'" + employee_id + "\'")
					return "Output String terminated due to KeyError"
			# concatenate the right and left string with the manager in the middle
			return output_string + manager.generate_output_string() + right_string
		else:
			# the root is the furthest right needed
			return output_string + manager.generate_output_string()

	def validate_employee(self, employee):
		""" normalise and check the initial """
		if not isinstance(employee, TreeNode):
			# if employee is a string then normalise it, check that it is in the tree and return the node
			entry = self.remove_whitespace(employee)
			entry = self.lookup_entry(entry)
			return entry
		else:
			# if it is a tree node then this was called unnecessarily
			return employee[0]

	def find_path(self, employee):
		""" Creates the path for the left hand side of the output string by bubbling up through the tree till the root
		node is found """
		return_list = []
		while employee.getManagerID() in self.id_lookup:
			# while manager ID is still an employee then create the return list
			return_list = return_list + [employee.getEmployeeID()]
			employee = self.id_lookup[employee.getManagerID()]
			if isinstance(employee, list):
				employee = employee[0]
		# add the highest manager to the return list
		return_list = return_list + [employee.getEmployeeID()]
		return return_list


# MAIN EXECUTION

# argument 1 is the path to the python file
if len(sys.argv) == 1:
	# if there just 1 input then ask for all inputs to be given
	file_path = raw_input("No file path specified, please enter a file path: ")
	first_entry = raw_input("No employee name\'s were entered, please enter the first employee: ")
	second_entry = raw_input("No employee name\'s were entered, please enter the second employee: ")
	input_args = {
		'filePath': file_path
	}
elif len(sys.argv) == 2:
	# if provided with 2 arguments it is assumed that the file path is provided (this assumption will be caught if
	# incorrect and the employee name is not a file name) ask for the employee names to be re-entered
	first_entry = raw_input("No employee name\'s were entered, please enter the first employee: ")
	second_entry = raw_input("No employee name\'s were entered, please enter the second employee: ")
	input_args = {
		'filePath': str(sys.argv[1])
	}
elif len(sys.argv) == 3:
	# if 3 arguments are provided we are to assume that the 3rd argument is the right most employee to be outputted
	# ask for the left most employee to be inputted
	first_entry = str(sys.argv[2])
	second_entry = raw_input("Only one employee name was entered, please enter the second employee: ")
	input_args = {
		'filePath': str(sys.argv[1])
	}
elif len(sys.argv) == 4:
	# if 4 arguments are given assume that they are in the correct order. If there is a problem the program will try
	# to rectify it if noticed
	first_entry = str(sys.argv[2])
	second_entry = str(sys.argv[3])
	input_args = {
		'filePath': str(sys.argv[1])
	}
# Initialise the tree
employeeTree = Tree(input_args)

# print out the output string generated by the tree
outputString = employeeTree.create_output(first_entry, second_entry)
print("\n\r Output String \n\r")
print(outputString)
