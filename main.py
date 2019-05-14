from request import Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uncurl
import requests
import uncurl
import time
import json
import re
from pathlib import Path

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

	# check if user passed a json file with variables to replace
	has_variables = ask_user_inform_json_file_with_variables()
	variables = get_json_file_content(has_variables)

	# read column0 to get the names
	descriptions = worksheet.col_values(2)

	# read colum1 to get the curls 
	curls = worksheet.col_values(3)

	# removing header
	descriptions.pop(0)
	curls.pop(0)

	print_line_break()

	# converting curls in requests	
	print("---------------- Starting converting CURL to python request ------------------")
	for i in range(len(curls)):
		try:
			curls[i] = handle_curl_string_before_parse(curls[i])
			if has_json_variable_file(has_variables):
				curls[i] = replace_variables_json_content(variables,curls[i])
			else:
				check_if_user_forgot_to_pass_json_file(curls[i])

			py_requests.append(uncurl.parse(f"""{curls[i]}"""))
			print(f'Convertion of test \" {descriptions[i]} \" ---> completed')
		except Exception as e:
			print(f"Failing parsing test \" {descriptions[i]} \" Cause --> {e}")
			py_requests.append("")
		time.sleep(1)

	print_line_break()

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
		time.sleep(1)
		print(msg.format(descriptions[i]))

	line_position = 2
	for i in range(len(list_response)):
		response = list_response[i]
		if response != None:
			worksheet.update_cell(line_position, 6, response.status_code)
			worksheet.update_cell(line_position, 4, response.text)
		line_position += 1

def ask_user_inform_json_file_with_variables():
	has_variables = input('Does this spreadsheet has some variable in the CURL? (y/n) : ')
	while has_variables.lower() != 'y' and has_variables.lower() != 'n':
		has_variables = input('Please inform using y or n: ')

	return has_variables

def get_json_file_content(has_variables):
	variables = None
	if has_json_variable_file(has_variables):
		json_path  = input('Inform the path of the JSON file with the variables: ')
		
		file_valid = False
		while file_valid == False:
			config = Path(json_path)
			if config.is_file and config.suffix == '.json':
				file_valid = True
			else:
				json_path  = input('Could not find the file or is not a JSON file. inform the correct path: ')


		
		with open(json_path) as json_file:
			data_json = json.load(json_file)
			variables = data_json
	return variables



def has_json_variable_file(has_variables):
	return has_variables.lower() == 'y'



def check_if_user_forgot_to_pass_json_file(curl):
	result = re.findall(r'{{.+}}', curl, re.MULTILINE)
	if result != []:
		raise Exception(f'This curls has the variable(s) {result} and no JSON file was informed, please inform one with this variables.')



def replace_variables_json_content(variables, val):
	matches = re.findall(r'{{.+}}', val, re.MULTILINE)
	msg_failed = ''
	for m in matches:
		key_catalog =  m.replace('{','').replace('}','')
		if(variables.get(key_catalog) != None):
			val = val.replace(m, variables.get(key_catalog))
		else:
			msg_failed += f'key {m} was not found in JSON file \n'

	if msg_failed != '':
		raise Exception(rreplace(msg_failed,'\n',''))
	return val


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



def print_line_break():
	print('\n\n\n')



def rreplace(s, old, new):
    return (s[::-1].replace(old[::-1],new[::-1], 1))[::-1]



if __name__ == "__main__":
	main()
