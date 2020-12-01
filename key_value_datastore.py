import operations
from time import sleep
import threading
import operations
import logging
import threading
import json  
#import json
import os
import sys
from cachetools import TTLCache 


logging.basicConfig(filename='datastore_app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

lock = threading.RLock()

def create1(client, key, value, **kwargs):
	ttl_value = kwargs.get('ttl', None)
	
	filepath = kwargs.get('filepath', ".//")
	with lock:
		if isinstance(value, str):
			try:
				value = json.loads(value)
			except:
				value = value
		
		status = create_operation(client, key, value, filepath = filepath , ttl = ttl_value)
		
		if 'successfull' in status:
			return "Create Operation Done"
		elif 'denied' in status:
			logging.error(status)
			return "Error occurred while creating : " + status
		else:
			logging.error(status)
			return "Error Status : " + status


def delete1(client, key, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	with lock:
		status = delete_operation(client, key, filepath = filepath)
		if 'Deleted' in status:
			return status
		elif 'not found' in status:
			logging.error(status)
			return status
		else:
			logging.error(status)
			return "Error Status : " + status


def read1(client, key, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	with lock:
		status = read_operation(client, key, filepath = filepath)
		if 'not found' in status:
			logging.error(status)
			return status
		elif 'value' in status:
			return status
		else:
			logging.error(status)
			return "Error Status : " + status


def reset1(client, **kwargs):
	filepath = kwargs.get('filepath', "")
	with lock:
		status = reset_operation(client, filepath = filepath)
		logging.info(status)
		return status



def create_operation(client_name, key, value, **kwargs):
	ttl_value = kwargs.get('ttl', None) 
	filepath = kwargs.get('filepath', ".//")
	try:
		with open(filepath+client_name+'.json', 'r+') as create_append:
			old_data = json.load(create_append)
			new_data = old_data
			creation_output = datastore_creation(new_data, key, value, client_name, filepath = filepath, ttl = ttl_value)
			if isinstance(creation_output, dict):
				new_data.update(creation_output)
				if 'Healthy' in validate(client_name, filepath = filepath):
					status = dumping_util(client_name, new_data, filepath = filepath)
					if 'Healthy' in validate(client_name, filepath = filepath) and 'Dumped' in status:
						return "Create Operation successfull-append"
					elif 'Failed' in status:
						return "Create Operation Failed - Data Dumping failed"
					else:
						with open(filepath+client_name+'.json','w+') as append:
							json.dump(old_data, append)
						return "Create Operation denied-append-(Insufficient space) | Client File execeeds 1 GB"
				else:
					return validate(client_name, filepath = filepath)
			else:
				return creation_output

	except FileNotFoundError as e:
		return new_client_creation(client_name, key, value, filepath = filepath, ttl = ttl_value)
 


def new_client_creation(client_name, key, value, **kwargs):
	ttl_value = kwargs.get('ttl', None)
	filepath = kwargs.get('filepath', ".//")
	datastore = {}				#New client so datastore is empty
	creation_output = datastore_creation(datastore ,key, value, client_name, filepath = filepath, ttl = ttl_value)
	if isinstance(creation_output, dict):
		status = dumping_util(client_name, creation_output, filepath = filepath)
		if 'Healthy' in validate(client_name, filepath = filepath) and 'Dumped' in status:
			return "Create Operation successfull-new"
		elif 'Failed' in status:
			return "Create Operation Failed - Data Dumping failed" 
		else:
			status = reset_operation(client_name, filepath = filepath)
			if 'removed' in status:
				return "Create Operation denied-new-(Insufficient space) | Client File execeeds 1 GB"
			return validate(client_name, filepath = filepath)
	else:
		return creation_output 

def datastore_creation(existing_datastore, key, value, client, **kwargs):
	ttl_value = kwargs.get('ttl', None)
	filepath = kwargs.get('filepath', ".//")
	datastore = {}
	key_existience = check_key_exist(existing_datastore, key, client)
	if 'New' in key_existience:
		status = key_value(key, value)
		if 'met' in status:
			if not isinstance(ttl_value, int) :
				datastore[key] = [value, 0]
			else:
				client = ttl_create(client, key, value, ttl_value)
				datastore[key] = [value, 1]
			return datastore
		else:
			if 'Value' in status and isinstance(value, dict):
				constrain_status = "Value size limit is 16KB, But it has {} KB".format(int(sys.getsizeof(value))/1000)
				
			elif not isinstance(value, dict):
				constrain_status = "Value's datatype should be JSON object (Dict)"
				
			elif 'Key' in status and isinstance(key, str):
				constrain_status = "Character limit for Key is 32, But it has {}".format(len(str(key)))
				
			else:
				constrain_status = "Key's datatype should be String"
			return constrain_status
	else:
		constrain_status = "Key | {} | already exist , value - {} ".format(key, existing_datastore[key][0])
		return constrain_status


def read_operation(client_name, key, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	try:
		with open(filepath+client_name+'.json','r+') as read_line:
			if read_line:
				data = json.load(read_line)	
			key_existience = check_key_exist(data, key, client_name)
			if 'exist' in key_existience:
				return "For key | "+ key +" | value  - {} ".format(data[key][0])
			elif 'expired' in key_existience:
				return key_existience
			else:
				return "Key | {} | not found for client - {} ".format(key, client_name)
				
	except FileNotFoundError as e:
		return '{} - Client_file_doesnot_exist'.format(client_name)


def delete_operation(client_name, key, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	try:
		with open(filepath+client_name+'.json','r+') as read_line_key:
			data = json.load(read_line_key)
			key_existience = check_key_exist(data, key, client_name)
			if 'exist' in key_existience:
				del data[key]
				status = dumping_util(client_name, data, filepath = filepath)
				if 'Dumped' in status:
					return "For key | "+ key +" | value - is deleted"
				else:
					return "Delete Operation Failed due to Data Dumping "					
			elif 'expired' in key_existience:
				return key_existience
			else:
				return "Key | {} | not found for client - {} ".format(key, client_name)
				
	except FileNotFoundError as e:
		return '{} - Client file doesnot exist'.format(client_name)


def reset_operation(client_name, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	try:
		os.remove(filepath+client_name+".json")
		return 'File removed!!!! - '+filepath+client_name

	except FileNotFoundError as e:
		return '{} - Client_file_doesnot_exist'.format(filepath+client_name)

####################### Utils ################################

def validate(file, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	try:
		size = os.path.getsize(filepath+file+".json")
		if int(size) < 1073741824:
			return filepath+file+'.json is less than 1 GB (Healthy)'
		else:
			return filepath+file+'.json is more than 1 GB (Unhealthy)'
	except OSError :
		return "File '%s' does not exists or is inaccessible" %(filepath+file+".json")

cache_global = "TTLCache([('ye', 'hide')], maxsize=1024, currsize=1)" ###Dummy value for cache


def ttl_create(client, key, value, ttl_value):
	cache = TTLCache(maxsize=1024, ttl=ttl_value)
	cache[key] = value
	global cache_global
	cache_global = cache
	return client


def time_to_live_check(client, key):
	global cache_global
	cache = cache_global
	try:
		if cache[key]:
			return 'key lives'
	except:
		return 'TTL Value for the Key - {} expired for the client - {}'.format(key,client)
		

def key_value(key, value):
	if isinstance(key, str) and len(str(key)) <= 32:
		if sys.getsizeof(value) <= 16000 and isinstance(value, dict):
			return "Key & Value constraints are met"
		else:
			return "Value constraints failed"
	else:
		return "Key constraints failed"


def check_key_exist(dict, key, client_name):
	if key in dict:
		ttl_status = "no_ttl"
		if dict[key][1] == 1 : ttl_status = time_to_live_check(client_name, key)
		if 'lives' in ttl_status:
			return "Key exist"
		elif 'no_ttl' in ttl_status:
			return "Key exist"
		else:
			return ttl_status
	else:
		return "New key"


def dumping_util(client_name, data, **kwargs):
	filepath = kwargs.get('filepath', ".//")
	if data:
		try:
			with open(filepath+client_name+'.json','w+') as line_data:
				json.dump(data, line_data)
				return 'Data Dumped into file'
		except:
			return 'Failed to dump into file'
	else:
		try:
			reset_operation(client_name, filepath = filepath)
			return 'Data Dumped into file'
		except:
			return 'Failed to dump into file'



class crd_unit:
	client = "freshworks"

	key = "backend_assessment"    
	key_int = 18
	key_more_than_32 = "This assessment is only for Engineer Role..."
    
	value_dict = {"Registered_candidate" : 
	{ 
   "college_name":"SVCE",
   "location":"Chennai",
   "departments":{ 
      "Department-1":"Information Technology",
      "Department-2":"Computer Science",
      "Department-3":"Bio Technology"
   }
   }
   }
	value_json_type = { "Student_name":"Shobiya", "status":"Final year", "Department":"Information Technology" }
	value_string = "Bommanhalli, Tavarekere and Madiwala"
	ttl_value = 10


def create(crd):
	print(create1(crd.client, crd.key, crd.value_json_type)+"\n\n")			
	print(create1(crd.client, crd.key_int, crd.value_json_type)+"\n\n")			
	print(create1("pinky", "student1", crd.value_dict)+"\n\n")				
	print(create1(crd.client, crd.key_more_than_32, crd.value_json_type)+"\n\n")
	print(create1("87Lane", crd.key_int, crd.value_string)+"\n\n")				
	print(create1("pinky", "student1", crd.value_dict)+"\n\n")			
	print(create1(crd.client, "Executive", crd.value_dict, ttl = crd.ttl_value)+"\n\n")	


def read(crd):
	print(read1(crd.client, crd.key)+"\n\n")									
	print(read1("pinky", "student1")+"\n\n")								
	print(read1("SVCE", crd.key)+"\n\n")										
	print(read1(crd.client, "Executive")+"\n\n")								
	print("\nSleeping mode...\n\n")
	sleep(20)
   # print(main.read(crd.client, crd.key)+"\n")		
	print(read1(crd.client, "Executive")+"\n\n")								


def delete(crd):
	print(delete1(crd.client, crd.key)+"\n\n")									
	print(delete1(crd.client, crd.key_more_than_32)+"\n\n")					
	print(delete1("Special24", crd.key)+"\n\n")									
	print(delete1(crd.client, crd.key)+"\n\n")								


def create_2(crd):
	print(create1("sherlock", crd.key, crd.value_json_type)+"\n\n")


def delete_2(crd):
	print(create1("sherlock", crd.key, crd.value_dict)+"\n\n")
	print(delete1("sherlock", crd.key)+"\n\n")


def crd_unit_begin(crd):
	
	print( "\n\n*************** Create mode crd test units ***************\n\n")
	create(crd)
	print( "\n\n*************** Read mode crd test units ***************\n\n")
	read(crd)
	print( "\n\n*************** Delete mode crd test units ***************\n\n")
	delete(crd)
	print( "\n\n*************** Reset mode crd test units ***************\n\n")
	print(reset1(crd.client))
	print(reset1("87Lane"))

if __name__ == "__main__": 
    
    print("\n######## General Test ########\n\n")
    crd = crd_unit()
    crd_unit_begin(crd)

    print("\n######## Thread-Safe Code Test ########\n\n")
    
    t1 = threading.Thread(target=create_2, args=(crd,)) 
    t2 = threading.Thread(target=delete_2, args=(crd,)) 
  
    t1.start() 
    t2.start() 
   
    t1.join() 
    t2.join() 
  
     
    print("Thread-safe Testing done")
