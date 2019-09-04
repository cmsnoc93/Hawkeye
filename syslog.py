def check_syslog(ssh,nme,version,fhand,devicedict):
    
    boo=True
	while boo:		
		try:
			time1 = ssh.send_command("show clock")
			boo=False
		except:
			print("9-4 Exception handled. sh clock. Trying again")
			boo=True
		print("Time ")
		print(time1)
		if not time1:
			boo=True
			print("9-4 Return from show clock not proper. Trying again ")
		elif not(isinstance(time1,str)):
			print("9-4  Return from show clock in not string. Trying again")
			boo=True
		elif len(time1.split())<5:
			print("Time received not proper. Trying again ")
			boo=True
		else:
			boo=False
	
	
	time1=time1.split(" ")[3:5]
	day = time1[0]+" "+time1[1]
	print("day: ",day)
	#ret = src.send_command("show log | i down|Down|up|Up|err|fail|Fail|drop|crash|MALLOCFAIL|duplex",time[0]+" "+str((int(time[1])-1)))

	boo=True
	while boo:
		try:
			if(version=="cisco_nxos"):
				ret=ssh.send_command("show logging | i err|drop|fail|Fail|crash|MALLOCFAIL|down")
				fhand.write("show logging | i err|drop|fail|Fail|crash|MALLOCFAIL|down\n")
			else:
				ret = ssh.send_command("show log | i err|drop|fail|Fail|crash|MALLOCFAIL|down")
				fhand.write("show log | i err|drop|fail|Fail|crash|MALLOCFAIL|down\n")
			boo=False
		except:
			print("9-5 exception handled in show log. Trying again ")
			boo=True
		if not(isinstance(ret,str)):
			print("9-5  Return from show log in not string. Trying again")
			boo=True
		else:
			boo=False
	
	array = ret.split('\n')

	
	fhand.write("Current Day: "+day)
	
	flaps=dict()
	count=0
	limit = 30 # Fetch the last N log
	syslog = dict()
	for line in array:
		if line.find("Syslog logging")==-1:
			if line.find('NBRCHANGE')!=-1:
				print(line)
				ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',line).group()
				print(ip)
				if not ip in flaps:
					flaps[ip]=1
				else:
					flaps[ip]+=1
				
			syslog.update({count:line})
			count+=1
			fhand.write(str(count)+": "+line+"\n")
			limit=limit - 1
			if limit == 0:
				break;
			
	devicedict.gennodedict['log']=syslog
	fhand.write('\n'+json.dumps(flaps))
	print(syslog)
	if(count == 0):
		fhand.write("\nNo Logs")
	fhand.write("\n\n")

	return devicedict