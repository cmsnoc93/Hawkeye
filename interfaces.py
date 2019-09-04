def check_interfaces(ssh,nme,verison,devicedict):
	for interf in devicedict.dictint.keys():
		devicedict.dictint[interf]['crc']=list()
		devicedict.dictint[interf]['duplex']=list()
		devicedict.dictint[interf]['description']=list()
		devicedict.dictint[interf]['reliability']=list()
		devicedict.dictint[interf]['txload']=list()
		devicedict.dictint[interf]['rxload']=list()
		devicedict.dictint[interf]['speed']=list()
		devicedict.dictint[interf]['collisions']=list()
		devicedict.dictint[interf]['late_collision']=list()
		devicedict.dictint[interf]['overrun']=list()
		devicedict.dictint[interf]['interf_reset']=list()
		devicedict.dictint[interf]['input_errors']=list()
		devicedict.dictint[interf]['output_errors']=list()
		devicedict.dictint[interf]['frame']=list()
		devicedict.dictint[interf]['ignored']=list()
		devicedict.dictint[interf]['bandwidth']=list()
		devicedict.dictint[interf]['output_drops']=list()

		print("Fetching :",interf)
		for iter in range(3):
			time.sleep(1)
			boo=True
			while boo:
				try:
					ret=ssh.send_command("sh interface "+interf,use_textfsm=True)
					boo=False
				except:
					print("11 Exception Raised , Trying again")
					boo=True
					continue
				print(ret)
				if not ret:
					boo=True
				elif isinstance(ret,str):
					print("11 output not in proper form, trying again ")
					boo=True
				else:
					boo=False
		
			print(ret)
			fhand.write("Show interface "+interf+" \n")
			fhand.write(str(ret))
			fhand.write("\n\n")
			line={}
			for line in ret:
				x=line.keys()
				if 'crc' in x:
					devicedict.dictint[interf]['crc'].append(line['crc'])
				if 'duplex' in x:
					devicedict.dictint[interf]['duplex'].append(line['duplex'])
				if 'description' in x:
					devicedict.dictint[interf]['description'].append(line['description'])
				if 'reliability' in x:
					devicedict.dictint[interf]['reliability'].append(line['reliability'])
				if 'txload' in x:
					devicedict.dictint[interf]['txload'].append(line['txload'])
				if 'rxload' in x:
					devicedict.dictint[interf]['rxload'].append(line['rxload'])
				if 'speed' in x:
					devicedict.dictint[interf]['speed'].append(line['speed'])
				if 'collisions' in x:
					devicedict.dictint[interf]['collisions'].append(line['collisions'])
				if 'late_collision' in x:
					devicedict.dictint[interf]['late_collision'].append(line['late_collision'])
				if 'overrun' in x:
					devicedict.dictint[interf]['overrun'].append(line['overrun'])
				if 'interf_reset' in x:
					devicedict.dictint[interf]['interf_reset'].append(line['interf_reset'])
				if 'input_errors' in x:
					devicedict.dictint[interf]['input_errors'].append(line['input_errors'])
				if 'output_errors' in x:
					devicedict.dictint[interf]['output_errors'].append(line['output_errors'])
				if 'frame' in x:
					devicedict.dictint[interf]['frame'].append(line['frame'])
				if 'ignored' in x:
					devicedict.dictint[interf]['ignored'].append(line['ignored'])
				if 'bandwidth' in x:
					devicedict.dictint[interf]['bandwidth'].append(line['bandwidth'])
				if 'output_drops' in x:
					devicedict.dictint[interf]['output_drops'].append(line['output_drops'])
	return devicedict