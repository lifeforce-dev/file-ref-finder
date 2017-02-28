import os
import sys
import re
import argparse
import mmap

def clear_logs():
	if os.path.exists(no_reference_log_name):
		open(no_reference_log_name, 'w').close()

def file_not_empty(file):
	return os.stat(file).st_size > 0

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

def build_ref_list(ref_list):
	# Gather all of the .png filenames and append to our reference list.
	for root, dirs, files in os.walk(args.ref_dir):
		for file in files:
			if ".png" in file:
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
			print "Found reference to: " + ref_base_name
			ref_list[ref] = True

# For every file in the search directory, mark the existence of all refs in the ref_list
def mark_references():
	# Determine which files contain at least one reference in any file from the root directory.
	for root, dirs, files in os.walk(args.search_dir):
		for file in files:
			if file_is_searchable(file) and file_not_empty(os.path.join(root, file)):
				print "Searching for references in " + file + "..."
				mark_references_in_file(root, file)

if __name__ == "__main__":
	# Command line args
	parser = argparse.ArgumentParser(description= 'Find file references in directory')
	parser.add_argument('-s', '--search_dir', help= 'Root directory of files potentially containing references.')
	parser.add_argument('-r', '--ref_dir', default= os.getcwd(), help= "Directory containing files we're looking for references of.")
	args = parser.parse_args()

	# We're searching for references to any of the files in this list.
	ref_list = {}
	search_extensions = [".ui", ".cpp", ".txt", ".json", ".css", ".h", ".qml"]

	# If we return no references to a file name, we will log it here.
	no_reference_log_name = os.path.join(os.getcwd(), "no-references.log")

	clear_logs()
	build_ref_list(ref_list)
	mark_references()
	for ref, found in ref_list.iteritems():
		print ref + " , " + str(found)
		if not found:
			log_no_reference(ref);
