from __future__ import print_function
import argparse
import subprocess
import string
import sys
from contextlib import contextmanager
import os
from GitPy import Git, MergeError

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

class BranchMerger:
	def __init__(self, git):
		self._git = git

	def merge_branches(self, branches, hook = None, no_merge = False):
		merge_errors = []
		for branch in branches:
			try:
				self._merge_branch(branch, hook, no_merge)
			except MergeError as merge_error:
				merge_errors.append(merge_error)
		return merge_errors

	def _merge_branch(self, branch, hook = None, no_merge = False):
		git = self._git
		try:
			branch = git.get_remote_branch_name(branch)
			print("Merging", branch)
			git.merge(branch, False)
			git.update_submodules()
			if git.has_changes():
				if no_merge:
					raise MergeError(branch, "Merge ignored", "")
				if hook:
					try:
						print("\tExecuting", hook)
						subprocess.check_call([hook], shell=True)
					except:
						raise MergeError(branch, "Hook failed: " + hook, "")
				git.commit()
		except:
			eprint("\tFailed to merge", branch)
			git.reset(True)
			raise

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("branch", nargs="*")
	parser.add_argument("--work-dir", help="Work tree path", metavar="<path>")
	parser.add_argument("--hook", help="Execute hook after merge", metavar="<command>")
	parser.add_argument("--no-merge", action="store_true", help="Do not merge branch")
	g = parser.add_mutually_exclusive_group()
	g.add_argument("-r", "--remote", default="origin", help="Specifies remote repository name", metavar="<name>")
	g.add_argument("-nr", "--no-remote", dest="remote", action="store_const", const=None, help="Merges local branches only")

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

def merge_branches(branches, remote = None, work_dir = None, hook = None, no_merge = False):
	git = Git(remote)
	merger = BranchMerger(git)

	if not branches:
		return
	
	with cd(work_dir):
		merge_errors = merger.merge_branches(branches, hook, no_merge)
		if not merge_errors:
			return

		eprint("Rejected branches:")
		for merge_error in merge_errors:
			eprint("\t{0.branch}, stdout: {0.stdoutdata!r}, stderr: {0.stderrdata!r})".format(merge_error))

def main():
	args = parse_args()
	merge_branches(args.branch, args.remote, args.work_dir, args.hook, args.no_merge)

main()