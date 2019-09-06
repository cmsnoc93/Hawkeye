import os
from cpu import check_cpu
from memory import check_memory
from showlog import check_syslog
from interfaces import check_interfaces
from protocols import check_protocols
from routeflaps import check_routeflaps
from spanningtree import check_spanningtree
from interfacecounters import check_interfacecounters


def fetchKPI(ssh,nme,logdir,devicedict):

	version = devicedict.gennodedict['version']['soft_ver']
	
	fname=(logdir+nme+".txt"))
	print(fname)
	fhand=open(fname,'w')

	# SHOW PROC CPU
	devicedict = check_cpu(ssh,nme,version,fhand,devicedict)

	# SHOW PROC MEMORY
	devicedict = check_memory(ssh,nme,version,fhand,devicedict)

	# SHOW LOG
	devicedict = check_syslog(ssh,nme,version,fhand,devicedict)

	# SHOW IP ROUTE
	devicedict = check_routeflaps(ssh,nme,version,fhand,devicedict)

	# SHOW INTERFACES
	devicedict = check_interfaces(ssh,nme,version,fhand,devicedict)

	# SHOW SPANNING TREE
	devicedict = check_spanningtree(ssh,nme,version,fhand,devicedict)

	# SHOW INTERFACE COUNTERS
	devicedict = check_interfacecounters(ssh,nme,version,fhand,devicedict)

	# SHOW IP PROTOCOLS (BGP/EIGRP)
	devicedict = check_protocols(ssh,nme,version,fhand,devicedict)

	forjson={}
	forjson['Name']=dict()
	forjson['Name']['0']=nme
	forjson['Interface Dictionary']=dict()

	forjson['Interface Dictionary']=devicedict.dictint
	forjson['General Node']=dict()
	print("Added key",forjson['General Node'])
	forjson['General Node']=devicedict.gennodedict
	
	ssh.disconnect()
	fhand.close()
	return forjson