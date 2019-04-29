class Request:

	def __init__(self, name, curl, response, status):
		self.name = name
		self.curl = curl
		self.response = response
		self.status = status
