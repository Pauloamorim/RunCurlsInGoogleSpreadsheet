from request import Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uncurl
import requests
import uncurl
import time
import json

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('PythonSheets-91c6e9d5b043.json', scope)

def main():
	gc = gspread.authorize(credentials)
	attempts = 1
	attempts_worksheet = 1
	py_requests = []

	# Getting the spreadsheet
	sht = get_spreadsheet(gc)
	while(sht == None):
		if(attempts == 3):
			print("3 invalids attempts, exiting script.")
			quit()

		attempts += 1
		print("Invalid key, we're not able to find a spreadsheet with this key.")
		sht = get_spreadsheet(gc)


	# Getting the worksheet
	worksheet = get_worksheet(sht)
	while(worksheet == None):
		if(attempts_worksheet == 3):
			print("3 invalids attempts, exiting script.")
			quit()

		attempts_worksheet += 1
		print("Invalid index, we're not able to find a tab with this index.")
		worksheet = get_worksheet(sht)


	has_variables = input('Does this spreadsheet has some variable in the CURL? (y/n) : ')
	while has_variables.lower() != 'y' and has_variables.lower() != 'n':
		has_variables = input('Please inform using y or n: ')

	if has_variables.lower() == 'y':
		json_path  = input('Inform the path of the JSON file with the variables: ')
		# TODO check when path is invalid
		variables = None
		with open(json_path) as json_file:
			data_json = json.load(json_file)
			variables = data_json

	# read column0 to get the names
	descriptions = worksheet.col_values(2)

	# read colum1 to get the curls 
	curls = worksheet.col_values(3)

	# removing header
	descriptions.pop(0)
	curls.pop(0)

	# converting curls in requests	
	for i in range(len(curls)):
		try:
			#TODO search for possible variables using re.findall(r"{{.+}}",x, re.MULTILINE) and if user provided json file, replace for the value
			curls[i] = handle_curl_string_before_parse(curls[i])
			py_requests.append(uncurl.parse(f"""{curls[i]}"""))
		except:
			print(f"Failing parsing test \" {descriptions[i]} \". CURL INVALID")
			py_requests.append("")


	print("---------------- Starting tests executions ------------------")
	list_response = []
	for i in range(len(py_requests)):
		msg = "Executing Test {} ..."
		if py_requests[i] != "":
			msg += " OK "
			exec('list_response.append({})'.format(py_requests[i]))
		else:
			list_response.append(None)
			msg += " Failed "

		print(msg.format(descriptions[i]))

	line_position = 2
	for i in range(len(list_response)):
		response = list_response[i]
		if response != None:
			worksheet.update_cell(line_position, 6, response.status_code)
			worksheet.update_cell(line_position, 4, response.text)
		line_position += 1



def handle_curl_string_before_parse(curl):
	return curl.replace("\\","").replace("-X","").replace("GET","").replace("POST","").replace("PUT","").replace("PATCH","")



def get_spreadsheet(gc):
	sheet_key = input("Inform the key of the spreadsheet: ")
	try:
		sht = gc.open_by_key(sheet_key)
		print(f"Spreadsheet {sht.title} returned")
		return sht
	except:
		return None


def get_worksheet(sht):
	worksheet_index = input("Inform the index of the tab inside the spreadsheet ( 0 index based ) : ")
	try:
		worksheet = sht.get_worksheet(int(worksheet_index))
		print(f"Tab {worksheet.title} returned")
		return worksheet
	except:
		return None





if __name__ == "__main__":
	main()
