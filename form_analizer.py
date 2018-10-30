"""
A tool for analizing HTML forms.

Author: Roberto Zoia roberto@zoia.org
License:  	GNU GENERAL PUBLIC LICENSE
            Version 3, 29 June 2007
            (Check LICENSE file)

Version:    0.1
Date:		2018-10-30

As the saying goes, 'If you are going to do it more than once, write a script to do it for you.'
"""

import sys

from termcolor import colored

import requests
import click
from bs4 import BeautifulSoup
from pprint import pprint


@click.command()
@click.option('--url', default=None, help='The url to parse.')

def main(url):
	
	if not url:
		print("ERROR:  You need to specify an url with the --url option.\n"
				"ERROR:  Exiting...")
		sys.exit(1)

	r = requests.get(url)
	if r.status_code == requests.codes.ok:
		parsed_data = parse(r)
		pretty_print(parsed_data)
	else:
		print("Could not fetch page at {}. Exiting.".format(url))
		sys.exit(1)


def pretty_print(o):
	if 'page' in o:
		pretty_print_page(o['page'])
	if 'forms' in o:
		for form in o['forms']:
			if form:  pretty_print_form(form)


def pretty_print_page(o):
	print("\n")
	print("Page information")
	print("="*40)
	
	for k, v in o.items():
		if k == 'cookies':
			print('*'*40)
			print(colored('COOKIES', 'green'))
			for cookie in v:
				print('{:20}  ==> {}'.format(cookie['name'], cookie['value'] ))
		else:	
			print('{:20}  ==> {}'.format(k, v))

	print("-"*40)

def pretty_print_form(o):
	print("\n")
	print(colored("FORM", 'green', attrs=['underline', ]))

	for k, v in o['form'].items():
		print('{:20}  ==> {}'.format(k,v))


	print(colored('FIELDS', 'green'))
	for field in o['input_fields']:
		pretty_print_field(field)
	print("-"*40)


def pretty_print_field(o):
	print('\n')
	for k, v in o.items():
		print('\t{:20}  ==> {}'.format(k,v))


def parse(r, parse_headers=False):
	"""
	Extracts the following data from the requests object and returns it as a dict:

		'page': a dict containing page information like url, cookies, etc.
		'forms':  a list of forms in the webpage

	(See other methods below for details.)

	"""

	result = {}

	result['page'] = parse_page_data(r, parse_headers)
	result['forms'] = parse_html(r)

	return result



def parse_page_data(r, parse_headers=False):
	
	result = {}
	result['url'] = r.url
	# cookies
	result['cookies'] = [{'name': i, 'value': v } for i, v in r.cookies.items()]

	if parse_headers:
		result['headers'] = [{'name': i, 'value': v } for i, v in r.headers.items()]

	return result


def parse_html(r):
	"""
	Receives a requests object and extract the relevant information from it.
	"""
	result = []

	soup = BeautifulSoup(r.text, 'html.parser')

	# Forms
	forms = soup.find_all('form')

	# Fields
	if forms:
		
		for form in forms:
			result.append(parse_form(form))

	return result


def parse_form(form):
	"""
	Extracts form attributes and input fields.
	"""
	if not form: return None

	result = {}

	result['form'] = parse_form_data(form)
	result['input_fields'] = parse_input_fields_data(form.find_all('input'))

	return result


def parse_form_data(form):
	"""
	Returns a dict with the form attributes specified in the 'tags' list.

	"""


	if not form: return None

	tags = [
		'method', 
		'action', 
		'id', 
		'enctype', 
		'class', 
	]
	result = { tag: form.attrs[tag] for tag in tags if tag in form.attrs }
	return result


def parse_input_fields_data(input_fields):
	"""
	Returns a list containing the input fields in the form.
	"""

	if not input_fields: return None
	result = [ parse_input_field(input_field) for input_field in input_fields if input_field]
	return result


def parse_input_field(input_field):
	"""
	Returns a dict with the field attributes specified in the tags list.
	"""	
	if not input_field: return None

	tags = [
		'name',
		'type',
		'id',
		'value',
		'class'
	]
	result = { tag: input_field.attrs[tag] for tag in tags if tag in input_field.attrs }
	return result



if __name__ == '__main__':
	main()



