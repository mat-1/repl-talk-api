def builtin_to_graphql(item):
	if isinstance(item, list) or isinstance(item, tuple) or isinstance(item, set):
		value = Field(*item)
	elif isinstance(item, dict):
		value = Field(item)
	else:
		value = str(item)
	return value


class Alias():
	def __init__(self, alias, field):
		self.alias = alias
		self.field = field

	def __repr__(self):
		return f'{self.alias}: {self.field}'


class Field():
	def __init__(self, *data, args={}, **kwargs):
		self.data = data or (kwargs.get('data'),)
		self.args = args

	def __str__(self):
		output = ''

		for item in self.data:
			if isinstance(item, str):
				output += item + ' '
			elif isinstance(item, Field):
				output += str(item) + ' '
			elif isinstance(item, Alias):
				output += str(item) + ' '
			elif isinstance(item, list) or isinstance(item, tuple):
				output += str(builtin_to_graphql(item)) + ' '
			else:
				for field in item:
					value = item[field]
					value = builtin_to_graphql(value)
					output += str(field)
					if self.args != {}:
						args_tmp = []
						for arg_key in self.args:
							arg_value = self.args[arg_key]
							args_tmp.append(f'{arg_key}: {arg_value}')
						output += '('
						output += ','.join(args_tmp)
						output += ')'

					output += '{'
					output += str(value)
					output += '}'
				output += ' '
		if output.endswith(' '):
			output = output[:-1]
		return output

	def __repr__(self):
		return self.__str__()


class Query():
	def __init__(self, name, args, data):
		self.field = Field({name: data}, args=args)

	def __str__(self):
		return 'query ' + str(self.field)
