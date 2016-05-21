#!/usr/bin/python
import json
import yaml #PyYAML


'''take supplied input (presumably some json returned from the nest api) & convert to the format of choice'''

def json_to_xml():
    '''Takes Nest API-output JSON and returns as XML'''
    pass

def json_to_yaml():
    '''Takes Nest API-output JSON and returns as YAML'''
    pass

def json_to_csv():
    '''Takes Nest API-output JSON and returns as CSV'''
    pass

def split_json():
	'''Takes Nest API-output JSON and returns a bunch of dictionaries'''


'''pseudocode for response:
	response = api_root + '?auth=' + token
	nest-json = json.loads(response.text)

	cameras-dict = nest-json['devices']['cameras']
	etc

	for key,value in cameras-dict.items():
		print(key)
		for sub-key,sub-value in value:
			print(sub-key)





#def json_to_json(input):
#    return(input)