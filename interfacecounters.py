import textfsm,time,re
from hawkutils import expand_name
def check_interfacecounters(ssh,nme,version,fhand,devicedict):
	print("For show interface counters")
	#print(devicedict.gennodedict['version']['hardware'])
	Int_count={}
	print(nme," ",devicedict.gennodedict['version']['soft_ver'])
	if devicedict.gennodedict['version']['soft_ver']=='cisco_ios':
		inter_dict=dict()
		for intface in devicedict.dictint.keys():
			inter_dict[intface]=dict()
			for j in range(0,3):
				ret1 = ssh.send_command("sh int counters error | inc "+intface)
				if not ret1:
					intfacek=expand_name(intface)
					if intfacek!=intface:
						inter_dict[intfacek]=dict()
						intfacek=intface
					ret1 = ssh.send_command("sh int counters error | inc "+intface)
					fhand.write("Show int counters error | ex 0\n")
					fhand.write(ret1)
					fhand.write("\n\n")
					inter_dict[intface][j]=list()
					if ret1:
						ret1=ret1.split('\n')
						for linex in ret1:
							if linex.split()[0]==intface:
								inter_dict[intface][j].append(linex.split()[1:])
						
		devicedict.gennodedict['interface_counters_errors']=inter_dict
		
				
	if devicedict.gennodedict['version']['soft_ver']=='cisco_nxos':                
		inter_dict={}
		for intface in devicedict.dictint.keys():
			inter_dict[intface]=dict()
			for j in range(0,3):
				ret1 = ssh.send_command("sh int counters error | inc "+intface)
				if not ret1:
					intfacek=expand_name(intface)
					if intfacek!=intface:
						inter_dict[intfacek]=dict()
						intfacek=intface
					ret1 = ssh.send_command("sh int counters error | inc "+intface)

				fhand.write("Show int counters error | ex 0\n")
				fhand.write(ret1)
				fhand.write("\n\n")
				inter_dict[intface][j]=list()
				if ret1:
					ret1=ret1.split('\n')
					for linex in ret1:
						if linex.split()[0]==intface:
							inter_dict[intface][j].append(linex.split()[1:])
		devicedict.gennodedict['interface_counters_errors']=inter_dict

	return devicedict