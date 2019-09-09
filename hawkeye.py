from flask import Flask, redirect, url_for, request, render_template, g, copy_current_request_context, current_app
from hawkutils import ThreadWithReturnValue, restructureDict, jsonifypath
from pathcalc import get_path
from kpis import fetchKPI
import json, os, shutil

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
					
					# Creating Log Directory for this Request
					processId = str(os.getpid())
					if os.path.exists(os.path.join('logs',processId)):
						print("Deleting Previous Logs")
						shutil.rmtree(os.path.join('logs',processId))
					os.makedirs(os.path.join('logs',processId))
					logdir = os.path.join('logs',processId)

					# Shoot threads for each device on the path
					for nme in setofnamest:
						ssh=g.dictofobj[nme].handle						
						thread = ThreadWithReturnValue(target=fetchKPI,args=(ssh,nme,logdir,g.dictofobj[nme]));
						threads.append(thread)
						print("Starting Thread :",thread)
						thread.start()
					
					# Wait for threads to return results
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


			# Forward Path
			try:
				#entry,exit,entryrev,setofnames,ping_stat = path_calc(src,dst)
				raise Exception()
			except:
				return list().append({'failure':'Failure occured in path calculation'})

			try:
				#g.intojson=callthreads(setofnames,1)
				raise Exception()
			except:
				return list().append({'failure':'Failure occured in KPI Analysis'})

			# Forward Path after SP Cloud
			if ping_stat['ssh_failure']=='true':
				entry2,exit2,entryrev2,setofnames2,ping_stat2=path_calc(dst,src)
				g.intojson2=callthreads(setofnames2,2) 

			# Path Connectivity Information
			print("Exit: ",exit,"\n")
			print("Reverse: ",entryrev,"\n")
			if ping_stat['ssh_failure']=='true':
				print("Exit2: ",exit2,"\n")
				print("Reverse2: ",entryrev2,"\n")

			paths1 = jsonifypath(exit,entryrev)
			device_json = restructureDict(g.intojson)

			# to do : change list to dictionary
			response_list = list()
			response_list.append(paths1) # response[0]
			response_list.append(device_json) # response[1]
			response_list.append(ping_stat) # response[2]
			
			# Add PID to response for finding correct log folder if requested
			worker = dict()
			worker['pid'] = os.getpid()
			response_list.append(worker) # response[3]

			# Response for Post-SP Path
			if ping_stat['ssh_failure']=='true':
				paths2 = jsonifypath(exit2,entryrev2)	
				device_json2 = restructureDict(g.intojson2)
				response_list.append(paths2) # response[4]
				response_list.append(device_json2) # response[5]
				response_list.append(ping_stat2) # response[6]

			print(os.getpid(),"Exiting")
			return json.dumps(response_list)
	

@app.route('/logs/<workerpid>/<device_name>')
def fetchRaw(workerpid,device_name):
	f = open('logs/'+workerpid+'/'+device_name+".txt","r")
	data = f.read()
	data = data.replace('\n','<br/>')
	print("Sending File")
	return json.dumps(data)
	




	
