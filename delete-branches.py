from __future__ import print_function
import argparse
import subprocess
import string
import sys
from contextlib import contextmanager
import os
from GitPy import Git

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

class BranchDeleter:
	def __init__(self, git):
		self._git = git

	def _delete_branch(self, branch, force = False):
		try:
			self._git.delete_branch(branch, force)
		except:
			return;

	def _delete_branches(self, branches, force = False):
		for branch in branches:
			self._delete_branch(branch, force)


	def delete_branches(self, branches, merged, force, keep = []):
		if not keep:
			keep = []

		if merged and not branches:
			branches += self._git.get_merged_branches()

		self._delete_branches(list_difference(branches, keep), force)

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("branches", nargs="*", metavar = "<branch>")
	parser.add_argument("--work-dir", help="Work tree path", metavar="<path>")
	parser.add_argument("--merged", action="store_true", help="All local merged branches")
	parser.add_argument("--force", action="store_true", help="Force branch deletion (even if not merged)")
	parser.add_argument("--keep", nargs="+", metavar="<branch>", help="Do not delete branch")

	args = parser.parse_args()
	return args

@contextmanager
def cd(new_dir):
	if new_dir:
		prev_dir = os.getcwd()
		os.chdir(os.path.expanduser(new_dir))
		try:
			yield
		finally:
			os.chdir(prev_dir)
	else:
		yield

def list_difference(a, b):
	return list(set(a) - set(b))

def delete_branches(branches = None, work_dir = None, merged = None, force = None, keep = None ):
	git = Git()
	deleter = BranchDeleter(git);
	with cd(work_dir):
		deleter.delete_branches(branches, merged, force, keep)
		return

def main():
	args = parse_args()
	delete_branches(args.branches, args.work_dir, args.merged, args.force, args.keep)

main()