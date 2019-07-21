class X:
	def __init__(self):
		self._x = {'x':1}

	def __getitem__(self, val):
		return self._x[val]

errors = X()

print(errors['x'])