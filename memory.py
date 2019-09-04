def check_memory(ssh,nme,version,fhand,devicedict):
    
	boo=True
	while boo:
		
		try:
			if(version=="cisco_nxos"):
				ret = ssh.send_command("show proc mem shared | include totals")
				fhand.write("Show proc mem shared | inc totals\n")
			else:
				ret = ssh.send_command("show proc mem | include Total")
				fhand.write("Show proc mem | inc totals\n")
			boo=False
		except:
			print(" 9-4 Exception handled in sh proc mem | inc Pool Total. Trying Again")
			boo=True
		print("Return from show proc mem ")
		print(ret)

		fhand.write(ret)
		fhand.write("\n\n")
		if not ret:
			print(" 9-4 Returned value is null. Trying again ")
			boo=True
		elif not(isinstance(ret,str)):
			boo=True
			print("9-4 Returned value is not string, trying again ")
		else:
			boo=False
		

	def mb(str):
		return round(int(str)/1024/1024,2)
				

	def percent(a,b):
		return round((int(a)/int(b)) * 100,2)
		
	memory = dict()
	ret = ret.split('\n')
	if version == "cisco_nxos":
		for line in ret:
			temp_vals = line.split(' ')
			vals = []
			for string in temp_vals:
				if len(string.strip())>0:
					vals.append(string)
			print(vals)
			memory.update({vals[0]:{'total':int(vals[5]),'used':int(vals[8]),'free':int(vals[11]),'percent':percent(vals[8],vals[5])}}) 
			break;

	else:
		count=0
		for line in ret:
			count=count+1
			if(count>2):
				break
			temp_vals = line.split(' ')
			vals = []
			for string in temp_vals:
				if len(string.strip())>0:
					vals.append(string)
			print(vals)
			memory.update({vals[0]:{'total':mb(vals[3]),'used':mb(vals[5]),'free':mb(vals[7]),'percent':percent(vals[5],vals[3])}})   

	devicedict.gennodedict['Process_Memory']=dict()
	devicedict.gennodedict['Process_Memory']=memory
	print(memory)
    return devicedict