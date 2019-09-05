import textfsm,time,re
def check_routeflaps(ssh,nme,version,fhand,devicedict):
    
		
	print("VERSION ",version)
	if version=='cisco_nxos':
		ret=ssh.send_command("sh ip route",use_textfsm=True)
		print(ret)
		fhand.write("Show ip route | i 00: \n")
		fhand.write(str(ret))
		fhand.write("\n\n")
		make_dict=dict()
		ct1=1
		for rou in ret:
			print(rou)
			if rou['uptime'][:2]=='00':
				print('\n')
				make_dict[ct1]=rou
				ct1+=1
		devicedict.gennodedict['ip_route_00']=make_dict
	else:
		boo=True
		while boo:
			try:
				ret=ssh.send_command("sh ip route")
				boo=False
			except:
				print("10 Exception Raised , Trying again")
				boo=True
			print(ret)
			if not ret:
				boo=True
			elif isinstance(ret,list):
				print("10 Return from sh ip route is a list, trying again")
				boo=True
			else:
				boo=False

		ret=ret.split('\n')
		gen={}
		ct1=0
		print("RETURN: " ,ret)
		for line in ret:
			print("LINE: ",line)
			line2=line.split()
			print("Splitted LINE: ",line2)
			if not(not(line2)) and line2[0]!='S' and line2[0]!='C' and line2[0]!='S*' and 'via' in line2 and (line2[0]=='D' or line2[0]=='B'):
				pos=line2.index('via')
				if line2[pos+2][0:2]=='00':
					ct1+=1
					gen[ct1]=line
					print(line)
					print("Yes")
		devicedict.gennodedict['ip_route_00']=gen
    
	return devicedict
