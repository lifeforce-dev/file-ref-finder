import sys
import re
import argparse
import mmap

# Command line args
parser = argparse.ArgumentParser(description= 'Find file references in directory')
parser.add_argument('-s', '--search_dir', help= 'Root directory of files potentially containing references.')
parser.add_argument('-r', '--ref_dir', default= os.getcwd(), help= "Directory containing files we're looking for references of.")
args = parser.parse_args()

# We're searching for references to any of the files in this list.
ref_list = []

# If we return no references to a file name, we will log it here.
no_reference_log_name = os.path.join(os.getcwd(), "no-references.log")

def clear_logs():
	if os.path.exists(no_reference_log_name):
		open(no_reference_log_name, 'w').close()

def log_no_reference(reference):
	# Append to end of file if it exists, otherwise create it.
	if os.path.exists(no_reference_log_name):
		fh = open(no_reference_log_name, "a")
	else:
		fh = open(no_reference_log_name, "w")

	fh.write("No references for " + reference + ".png\n")

def build_ref_list(ref_list):
	# Gather all of the .png filenames and append to our reference list.
	for root, dirs, files in os.walk(args.ref_dir):
		for file in files:
			if ".png" in file:
				ref_list.append(file)

def find_ref_in_file(root, file, pattern):
	with open(os.path.join(root, file), 'r+') as file_in:
		data = mmap.mmap(file_in.fileno(), 0)
		mo = re.search(pattern, data)
		if mo:
			return True

def find_reference(reference):
	found = False
	# Starting at the root, find all lines in every text file containing a reference
	for root, dirs, files in os.walk(args.search_dir):
		for file in files:
			if ".cpp" in file or ".txt" in file or ".json" in file or ".ui" in file:
				reference = os.path.splitext(reference)[0]
				regexPattern = r'(.*%s.*)' % reference
				found = find_ref_in_file(root, file, regexPattern)
				if found:
					print "Found reference in" + os.path.join(root, file)
	if not found:
		log_no_reference(reference)

def find_references():
	for ref in ref_list:
		print "finding references for " + ref
		find_reference(ref)

clear_logs()
build_ref_list(ref_list)
find_references()
