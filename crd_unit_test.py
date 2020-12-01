import main
#import operations
from time import sleep
import threading

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
	print(main.create(crd.client, crd.key, crd.value_json_type)+"\n\n")			
	print(main.create(crd.client, crd.key_int, crd.value_json_type)+"\n\n")			
	print(main.create("pinky", "student1", crd.value_dict)+"\n\n")				
	print(main.create(crd.client, crd.key_more_than_32, crd.value_json_type)+"\n\n")
	print(main.create("87Lane", crd.key_int, crd.value_string)+"\n\n")				
	print(main.create("pinky", "student1", crd.value_dict)+"\n\n")			
	print(main.create(crd.client, "Executive", crd.value_dict, ttl = crd.ttl_value)+"\n\n")	


def read(crd):
	print(main.read(crd.client, crd.key)+"\n\n")									
	print(main.read("pinky", "student1")+"\n\n")								
	print(main.read("SVCE", crd.key)+"\n\n")										
	print(main.read(crd.client, "Executive")+"\n\n")								
	print("\nSleeping mode...\n\n")
	sleep(20)
   # print(main.read(crd.client, crd.key)+"\n")		
	print(main.read(crd.client, "Executive")+"\n\n")								


def delete(crd):
	print(main.delete(crd.client, crd.key)+"\n\n")									
	print(main.delete(crd.client, crd.key_more_than_32)+"\n\n")					
	print(main.delete("Special24", crd.key)+"\n\n")									
	print(main.delete(crd.client, crd.key)+"\n\n")								


def create_2(crd):
	print(main.create("sherlock", crd.key, crd.value_json_type)+"\n\n")


def delete_2(crd):
	print(main.create("sherlock", crd.key, crd.value_dict)+"\n\n")
	print(main.delete("sherlock", crd.key)+"\n\n")


def crd_unit_begin(crd):
	
	print( "\n\n*************** Create mode crd test units ***************\n\n")
	create(crd)
	print( "\n\n*************** Read mode crd test units ***************\n\n")
	read(crd)
	print( "\n\n*************** Delete mode crd test units ***************\n\n")
	delete(crd)
	print( "\n\n*************** Reset mode crd test units ***************\n\n")
	print(main.reset(crd.client))
	print(main.reset("87Lane"))

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

