from __future__ import print_function
import argparse
import subprocess
import string
import sys
from contextlib import contextmanager
import os

class MergeError(Exception):
	def __init__(self, branch, stdoutdata, stderrdata):
		super(MergeError, self).__init__("MergeError")
		self.branch = branch
		self.stdoutdata = stdoutdata
		self.stderrdata = stderrdata
	
	def __str__(self):
		return "MergeError(branch: {0.branch}, stdout: {0.stdoutdata!r}, stderr: {0.stderrdata!r})".format(self)

class Git:

	def __init__(self, remote = None):
		self._remote = remote

	def merge(self, branch, commit = True):
		args = ["--no-ff", "--quiet", branch]
		if not commit:
			args.append("--no-commit")
		(stdoutdata, stderrdata, return_code) = self._executeEx("merge", args)
		if return_code:
			raise MergeError(branch, stdoutdata, stderrdata)

	def update_submodules(self):
		self._execute("submodule", ["update", "--init"])

	def has_changes(self):
		try:
			self._execute("diff", ["--quiet", "HEAD"])
			return False
		except Exception:
			return True

	def commit(self, message = None):
		args = ["--message", message] if message else ["--no-edit"]
		args.append("--quiet")
		self._execute("commit", args)

	def reset(self, hard):
		args = ["--hard"] if hard else []
		self._execute("reset", args)

	def abort_merge(self):
		try:
			self.merge("HEAD")
		except Exception:
			self._execute("merge", ["--abort"])

	def push(self):
		self._execute("push", ["--set-upstream", self._remote, self.get_current_branch()])

	def get_current_branch(self):
		(stdoutdata, stderrdata, _) = self._executeEx("rev-parse", ["--abbrev-ref", "HEAD"])
		return stdoutdata.splitlines()[0]

	def get_remote_branch_name(self, branch):
		return (self._remote + "/" + branch) if self._remote else branch

	def _execute(self, command, args = []):
		exec_params = ["git", command] + args
		subprocess.check_call(exec_params)

	def _executeEx(self, command, args = []):
		exec_params = ["git", command] + args
		proc = subprocess.Popen(exec_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdout, stderr) = proc.communicate()
		return (stdout, stderr, proc.returncode)

	def delete_branch(self, branch_name, force=False):
		args = ["-D" if force else "-d"];
		if type(branch_name) == str:
			args.append(branch_name)
		else:
			args += branch_name;
		self._execute("branch", args)

	def get_merged_branches(self):
		branch_names = str(self._executeEx("branch", ["--merged"])[0]).split('\n')
		merged_branches = []
		for branch in branch_names:
			if branch and not branch.startswith("*"):
				merged_branches.append(branch.strip())
		return merged_branches
