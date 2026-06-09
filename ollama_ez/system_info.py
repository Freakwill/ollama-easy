
"""
System information shown in the chatting.
"""

class SystemInfo:
	name = 'System'


class NotRegistered(SystemInfo):

	def __init__(cmd):
		self.cmd = cmd

	def __str__(self):
		return f"{self.name}: {self.cmd} is not registered yet!"


class SetParameter(SystemInfo):

	def __init__(val, attr):
		self.val = val
		self.attr = attr

	def __str__(self):
		return f'💻System: The parameter `{self.attr}` of chat object is set to be `{self.val}`.'


class SetAttribute(SystemInfo):

	def __init__(val, attr):
		self.val = val
		self.attr = attr

	def __str__(self):
		return f'💻System: The attribute `{self.attr}` of chat object is set to be `{self.val}`.'
