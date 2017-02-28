import os
import sys
import re
import argparse
import mmap

#/
# Utility functions
#/

# Clears stale logs.
def clear_logs():
	if os.path.exists(no_reference_log_name):
		open(no_reference_log_name, 'w').close()

def is_file_empty(file):
	return os.stat(file).st_size <= 0

# Returns if this file is one that we're allowed to look for.
def file_is_searchable(file):
	extension = os.path.splitext(file)[1]
	return  extension in search_extensions

def log_no_reference(reference):
	# Append to end of file if it exists, otherwise create it.
	if os.path.exists(no_reference_log_name):
		file = open(no_reference_log_name, "a")
	else:
		file = open(no_reference_log_name, "w")

	file.write("No references for " + reference + "\n")

#/
# Work functions
#/

def build_ref_list(ref_list):
	# Gather all of the files that meet our reference criteria and append to our ref list.
	for root, dirs, files in os.walk(args.ref_dir):
		for file in files:
			ext = os.path.splitext(file)[1]
			if ext in args.ref_extensions:
				ref_list[file] = False

# Return whether a given regex matches any line in the specified file.
def find_ref_in_file(root, file, pattern):
	with open(os.path.join(root, file), 'r+') as file_in:
		data = mmap.mmap(file_in.fileno(), 0)
		mo = re.search(pattern, data)
		if mo:
			return True

# For each ref in the ref_list, if a match is found in the current file, mark it.
def mark_references_in_file(root, file):
	for ref, found in ref_list.iteritems():
		# Don't bother searching for a reference we've already found before.
		if found:
			continue
		ref_base_name = os.path.splitext(ref)[0]
		regex_pattern = r'(.*%s.*)' % ref_base_name

		if find_ref_in_file(root, file, regex_pattern):
			print "Found reference to: " + ref + " in " + file
			ref_list[ref] = True

# For every file in the search directory, mark the existence of all refs in the ref_list
def mark_references():
	# Determine which files contain at least one reference in any file from the root directory.
	for root, dirs, files in os.walk(args.search_dir):
		for file in files:
			if file_is_searchable(file) and not is_file_empty(os.path.join(root, file)):
				print "Searching for references in " + file + "..."
				mark_references_in_file(root, file)

# Look through all of the data
def dump_results():
	print "Logging files that had no reference..."
	for ref, found in ref_list.iteritems():
		if not found:
			log_no_reference(ref);

if __name__ == "__main__":

	# Command line args
	parser = argparse.ArgumentParser(description= 'Find file references in directory. '
		'Default functionality is to find all images referenced in the text of the provided directory tree')
	required  = parser.add_argument_group('required arguments')

	# search_dir: This is required. We need to know which root directory to search in.
	required.add_argument('-s', '--search_dir',
		help= 'Root directory of files potentially containing references.', required = True)

	# Everything below here is optional.
	# ref_dir. We will assume the files we want references to are in this directory.
	parser.add_argument('-r', '--ref_dir', default= os.getcwd(),
		help= "Directory containing files we're looking for references of.")

	# search_extensions: We provide some sort of sane default.
	parser.add_argument('-f', '--search_extensions', nargs='*',
		default= [".ui", ".cpp", ".txt", ".json", ".css", ".h", ".qml"],
		help= 'Only files in this list of extensions will be searched. ex: .txt .cpp .h')

	# ref_extensions: We provide some sort of sane default.
	parser.add_argument('-e', '--ref_extensions', nargs='*',
		default= ['.png', '.jpg', '.mng', '.jpeg', '.gif'],
		help= 'Find references to all files with an extension in this list. ex: .jpg .png .jpeg')

	args = parser.parse_args()

	# We're searching for references to any of the files in this list.
	ref_list = {}
	search_extensions = args.search_extensions
	ref_extensions = args.ref_extensions

	# If we return no references to a file name, we will log it here.
	no_reference_log_name = os.path.join(os.getcwd(), "no-references.log")

	print "Clearing logs..."
	clear_logs()
	
	print "Building list of files you're searching for references of..."
	build_ref_list(ref_list)

	print "Working..."
	mark_references()

	dump_results()

	print "done."
