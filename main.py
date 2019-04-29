from request import Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uncurl
import requests
import uncurl
import time

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



	# read column0 to get the names
	descriptions = worksheet.col_values(1)
	
	# read colum1 to get the curls 
	curls = worksheet.col_values(2)

	# removing header
	descriptions.pop(0)
	curls.pop(0)

	# converting curls in requests	
	for curl in curls:
		# TODO handler when parse fails 
		py_requests.append(uncurl.parse(curl))

	list_response = []
	for i in range(len(py_requests)):
		print(f'Executing Test {descriptions[i]} ...')	
		exec('list_response.append({})'.format(py_requests[i]))

	line_position = 2
	for i in range(len(list_response)):
		response = list_response[i]
		worksheet.update_cell(line_position, 3, response.status_code) 
		worksheet.update_cell(line_position, 4, response.text) 
		line_position += 1


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
