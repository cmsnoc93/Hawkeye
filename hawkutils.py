from threading import Thread
from subprocess import Popen, PIPE

# Extended Thread Class that returns its callable's return values
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

# Device Class
class router(object):
	    def __init__(self,name):
	        self.name=name
	        self.entry=set()
	        self.exit=set()
	        self.dictint=dict()
	        self.gennodedict=dict()
	        self.sship=''
	        self.sshpass=False

	    def addentry(self,ent):
	        self.entry.add(ent)

	    def addconnect(self,conn):
	        self.handle=conn

	    def addsship(self,ipadd):
	        self.sship=ipadd

	    def addexit(self,ext):
	        self.exit.add(ext)

	    def adddictip(self,interf,ip):
	        if interf not in self.dictint.keys():
	            self.dictint[interf]=dict()
	        self.dictint[interf]['ip']=ip

	    def addsshpass(self,var):
	        self.sshpass=var

	    def objprint(self):
	        print(" Name "+self.name)
	        print(" Entry interfaces ")
	        print(self.entry)
	        print(" Exit interfaces ")
	        print(self.exit)
	        print(" Interface Dictionary ")
	        print(self.dictint)
	        print()
	        print(" General Node Information ")
	        print(self.gennodedict)	        
	        print("------------------------------")

# JSON formatting for KPIs
def restructureDict(kpi_json):
		device_json = []
		for device in kpi_json:
			processes = {}
			protocols = {}
			device_health= []
			device["device"] = dict()
			device["device"]["memory"]  =dict()
			device["device"]["log"] = dict()
			device["device"]["version"] = dict()
			device["device"]["interface_counters_errors"] = dict();
			device["CPU"] = dict()
			device["CPU"]["pid"] = dict()
			
			for key in device["General Node"].keys():
				if (key == "interface_counters_errors"):
					device["device"][key] = device["General Node"][key]
				if (key == "Process_Memory"):
					device["device"]["memory"] = device["General Node"][key]
				if(key == "log"):
					device["device"]["log"] = device["General Node"][key]
				if(key == "version"):
					device["device"]["version"] = device["General Node"][key]
				if (key == "CPU"):
					device["CPU"]["cpu_util"] = device["General Node"][key]
				if key.isdigit():
					processes[key] = device["General Node"][key]
					device["CPU"]["pid"] = processes
				if (key == "eigrp_neigh"):
					protocols["eigrp"] = device["General Node"][key]
				if (key == "bgp_neigh"):

					protocols["bgp"] = device["General Node"][key]
				if (key == "ip_route_00"):
					protocols["ip_route"] = device["General Node"][key]
				if (key == "spanning_tree"):
					protocols["spanning_tree"] = device["General Node"][key]
				device["Protocols"] = protocols
			del device["General Node"]
			device_json.append(device)
		return device_json

# JSON formatting for path
def jsonifypath(exit,reverse):
		temp = []
		for key,value in exit.items():
			value = list(value)
			if len(value)>0 :
				for i in value:
					t = {}
					t["now"] = key
					foo = i.split()
					t["exit"] = foo[0]
					try:
						foo2 = list(reverse[foo[1]])
				
					except:
						t["next"]="Couldnt Fetch"
						t["entry"]="Couldnt Fetch"	
						temp.append(t)
						break
					t["next"] = foo2[0].split()[0]
					t["entry"] = foo2[0].split()[1]
					temp.append(t)
			else:
					t = {}
					t["now"] = key
					foo = value[0].split()
					t["exit"] = foo[0]
					try:
						foo2 = list(reverse[foo[1]])
				
					except:
						t["next"]=["Couldnt Fetch"]
						t["entry"]=["Couldnt Fetch"]	
						temp.append(t)
						break			
					t["next"] = foo2[0].split()[0]
					t["entry"] = foo2[0].split()[1]
					temp.append(t) 		
		return temp

# Expand Interface Names
def expand_name(rec):
	if 'Ethernet' not in rec:
	    if rec[0:3]=="Eth":
	        snd="Ethernet"+rec[3:]
	    elif rec[0:2]=="Fa":
	        snd="FastEthernet"+rec[2:]
	    else:
	        snd="GigabitEthernet"+rec[3:]
	else:
	    if 'Gig'in rec:
	        snd='Gig'+rec[rec.find('net')+3:]
	    elif 'Fast'in rec:
	        snd='Fa'+rec[rec.find('net')+3:]
	    else:
	        snd='Eth'+rec[rec.find('net')+3:]
	print(" RECEIVED NAME "+rec+" CHANGED NAME "+snd+"\n\n\n\n\n")

# Ping
def _ping_to(check_dst):
	cmd="ping -c 4 "
	cmd+=check_dst
	p= Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	out,err= p.communicate()
	print(out)
	out=out.split()
	recv_index=out.index("received,".encode('ascii'))
	num_stat=int(out[recv_index-1].decode('ascii'))
	if num_stat>=3:
		status='perfect'
	elif num_stat>0:
		status='Not all pings going through'
	else:
		status='not reachable'
	return status