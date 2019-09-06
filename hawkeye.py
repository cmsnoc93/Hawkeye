from flask import Flask, redirect, url_for, request, render_template, g, copy_current_request_context, current_app
from hawkutils import ThreadWithReturnValue, restructureDict, jsonifypath
from pathcalc import get_path
from kpis import fetchKPI
import json, os

app = Flask(__name__)

# Template Engine Configuration
jinja_options = app.jinja_options.copy()
jinja_options.update(dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='<#',
    comment_end_string='#>'))
app.jinja_options = jinja_options


if __name__ == '__main__' :
	app.run(threaded=True)

@app.route('/Topology',methods=['GET','POST'])
def topology():

	with app.app_context():
		
		if request.method == 'GET':
			return render_template('topology.html')

		elif request.method == 'POST':

			# Inputs
			req = request.get_json()
			src = req['src']
			dst = req['dst']
			print("src:",src, " dst:",dst, "worker pid:",os.getpid())
				
			# Request-Specfic Data Structures
			g.dictofobj={}
			g.intojson=[]
			g.intojson2=[]
			
			# Path Calculation
			@copy_current_request_context
			def path_calc(src,dst):
				return get_path(src,dst)

			# KPIs
			@copy_current_request_context
			def callthreads(setofnamest,path_no):
				
					threads=[]
					print("Path number \n dict of objects ")
					print(g.dictofobj)
					
					processId = str(os.getpid())
					os.makedirs(os.path.join('logs',processId))
					logdir = os.path.join('logs',processId)

					for nme in setofnamest:
						ssh=g.dictofobj[nme].handle						
						thread = ThreadWithReturnValue(target=fetchKPI,args=(ssh,nme,logdir,g.dictofobj[nme]));
						threads.append(thread)
						print("Starting Thread :",thread)
						thread.start()
					
					for thread in threads:
						print("Waiting for thread to complete:")
						print(thread)
						if path_no == 1:
							g.intojson.append(thread.join())
						elif path_no == 2:
							g.intojson2.append(thread.join())
						
					if path_no == 1:
						return(g.intojson)
					elif path_no == 2:
						return(g.intojson2)


			entry,exit,entryrev,setofnames,ping_stat = path_calc(src,dst)
			g.intojson=callthreads(setofnames,1)
			if ping_stat['ssh_failure']=='true':
				entry2,exit2,entryrev2,setofnames2,ping_stat2=path_calc(dst,src)
				print("\n\n\n\n SET OF NAMES ")
				print(setofnames2)
				print("\n\n\n\n")
				g.intojson2=callthreads(setofnames2,2) 

			print("Exit: ",exit,"\n")
			print("Reverse: ",entryrev,"\n")
			if ping_stat['ssh_failure']=='true':
				print("Exit2: ",exit2,"\n")
				print("Reverse2: ",entryrev2,"\n")

			paths1 = jsonifypath(exit,entryrev)
			device_json = restructureDict(g.intojson)

			response_list = list()
			response_list.append(paths1) # response[0]
			response_list.append(device_json) # response[1]
			response_list.append(ping_stat) # response[2]
			
			worker = dict()
			worker['pid'] = os.getpid()
			response_list.append(worker) # response[3]

			if ping_stat['ssh_failure']=='true':
				paths2 = jsonifypath(exit2,entryrev2)	
				device_json2 = restructureDict(g.intojson2)
				response_list.append(paths2) # response[4]
				response_list.append(device_json2) # response[5]
				response_list.append(ping_stat2) # response[6]

			print(os.getpid(),"Exiting")
			return json.dumps(response_list)
	

@app.route('/log/<device_name>')
def fetchRaw(device_name):
	f = open(device_name+".txt","r")
	data = f.read();
	data = data.replace('\n','<br/>')
	print("Sending File")
	return json.dumps(data)
	




	
