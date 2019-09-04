def check_protocols(ssh,nme,version,fhand,devicedict):
    flag2=0
	flag1=0
	if version=='cisco_nxos':
		ret=ssh.send_command("sh feature | i eigrp",use_textfsm=True)
		print(ret)
		fhand.write("Show feature | i eigrp \n")
		fhand.write(str(ret))
		fhand.write("\n\n")
		eigrp_flag=0
		for moo in ret:
			if moo['state']=='enabled':
				#eigrp_flag=1
				flag2=1
				print("Enabled")
				break	        
	else:
		boo=True
		while boo:
			ans=ans1=0
			try:
				ans=ssh.send_command("show ip protocols | include bgp")
				ans1=ssh.send_command("show ip protocols | include eigrp")
				boo=False
			except:
				print("9-2 Exception raised in sh ip protocols, trying again ")
				boo=True
			print(" sh ip protocols | i bgp ")
			print(ans)
			print(" sh ip protocols | i eigrp")
			print(ans1)
			fhand.write("Show ip protocols | i bgp: \n")
			fhand.write(ans)
			fhand.write("\n\n")
			fhand.write("Show ip protocols | i eigrp \n")
			fhand.write(ans1)
			fhand.write("\n\n")
			if not(isinstance(ans,str)) or not(isinstance(ans1,str)):
				boo=True
				print("9-2 Return from sh ip protocols not proper. Trying again")
			elif not ans and not ans1:
				print("9-2  Return null from both protocols, trying again ")
				boo=True
			elif (not(ans1) and len(ans.split())<5) or (not(ans) and len(ans1.split())<5):
				print(" 9-2-1 Return from sh ip protocols not proper. Trying again")
				boo=True
			elif not(not(ans)) and len(ans.split())<5 and not(not(ans1)) and len(ans1.split())<5:
				print(" 9-2-3 Return from sh ip protocols not proper. Trying again")
				boo=True
			else:
				boo=False
			
	
		bgp=ans.split("\n")
		eigrp=ans1.split("\n")
		bgp_sub='"bgp'
		eigrp_sub='"eigrp'
		flag1=0
		flag2=0
		for text in bgp:
			if bgp_sub in text:
				flag1=1
				break
		for text in eigrp:
			if eigrp_sub in text:
				flag2=1
				break
	
	if flag2==1:
		devicedict.gennodedict['eigrp_neigh']=dict()
		if version=='cisco_nxos':
			
			neigh_wise_eig=dict()
			all_eig_neigh=set()
			e_size=list()
			for iterate in range(0,3):
				ret=ssh.send_command("sh ip eigrp neighbor")
				#print(ret)
				ret=ret.split('\n')[3:]
				print(" Nexus eigrp return")
				print(ret)
				e_size.append(len(ret))
				for retslip in ret:
					#print(retslip.split())
					retslip=retslip.split()
					print('\n')
					if retslip[1] not in all_eig_neigh:
						all_eig_neigh.add(retslip[1])
						neigh_wise_eig[retslip[1]]=list()
					interim_dict=dict()
					interim_dict={'e_neigh':retslip[1],'e_interf':retslip[2],'e_hold':retslip[3],'e_uptime':retslip[4],'e_srtt':retslip[5],'e_rto':retslip[6]}
					neigh_wise_eig[interim_dict['e_neigh']].append(interim_dict)
				time.sleep(1)


			for e_neigh in all_eig_neigh:
				e_fl1=0
				e_fl2=0
				e_fl3=0
				e_fl4=0
				e_fl5=0
				lneigh=len(neigh_wise_eig[e_neigh])
				last_iter=neigh_wise_eig[e_neigh][lneigh-1]
				last_iter['condition']=''
				for iterate in range (0,lneigh):
					if iterate>0 and e_fl1==0 and neigh_wise_eig[e_neigh][iterate]['e_srtt']!=neigh_wise_eig[e_neigh][iterate-1]['e_srtt']:
						e_fl1=1
						last_iter['condition']+=' srtt value fluctuating. '
					if iterate>0 and e_fl2==0 and neigh_wise_eig[e_neigh][iterate]['e_rto']!=neigh_wise_eig[e_neigh][iterate-1]['e_rto']:
						e_fl2=1
						last_iter['condition']+=' rto value fluctuating. '
					if e_fl4==0 and int(neigh_wise_eig[e_neigh][iterate]['e_srtt'])>1500:
						last_iter['condition']+=' srtt value very high. '
						e_fl4=1
					if e_fl5==0 and int(neigh_wise_eig[e_neigh][iterate]['e_rto'])>4500:
						last_iter['condition']+=' rto value very high. '
						e_fl5=1
					if e_fl3==0 and re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}$',neigh_wise_eig[e_neigh][iterate]['e_uptime']):
						et1=int(neigh_wise_eig[e_neigh][iterate]['e_uptime'][:2])*60*60+int(neigh_wise_eig[e_neigh][iterate]['e_uptime'][3:5])*60+int(neigh_wise_eig[e_neigh][iterate]['e_uptime'][6:])
						if et1<86400:
							e_fl3=1
							last_iter['condition']+=' uptime less than an hour. '
				if last_iter['condition']=='':
					last_iter['condition']='perfect.'
				devicedict.gennodedict['eigrp_neigh'][e_neigh]=dict()
				devicedict.gennodedict['eigrp_neigh'][e_neigh]=last_iter
			if e_size[0]>0 and (e_size[0]!=e_size[1] or e_size[1]!=e_size[2]):
				devicedict.gennodedict['eigrp_neigh']['Number_of_neigh']='Number of neighbors not constant'
				print(last_iter)
		else:
			print("eigrp there")
			# SHOW IP EIGRP NEIGHBORS (3)

			for iter in range(3):
					boo=True
					while boo:
						try:
							ans=ssh.send_command("show ip eigrp neighbors")
							boo=False
						except:
							print("9-3 Exception handled. Error in sh ip eigrp neigh. Trying again ")
							boo=True
	
						print(" Return from sh ip eigrp neighbors ")
						print(ans)
						fhand.write("Show ip eigrp neigh \n")
						fhand.write(ans)
						fhand.write("\n\n")
						if not ans:
							print('Null returned from show ip eigrp neighbors')
							boo=True
						elif not(isinstance(ans,str)):
							print('not a string, returned from show ip eigrp neighbors')
							boo=True
						elif len(ans.split())<3:
							print('size less, returned from show ip eigrp neighbors')
							boo=True
						else:
							boo=False

						boo=True
						while boo:
							try:
								template=open('cisco_ios_show_ip_eigrp_neighbors.template')
								res_template=textfsm.TextFSM(template)
								ans_final=res_template.ParseText(ans)
								boo=False
							except Exception as e:
								print(e)
								print("9-4 Exception in Textfsm, Trying again")
								boo=True
						print("\n TEXTFSM LIST:\n")	
						print(ans_final)
						hello={}
						j=0
						for i in range(0,len(ans_final)):
							hello={}
							neigh = hello['neighbor']=ans_final[i][1]
							hello['uptime'] = list()
							hello['uptime'].append(ans_final[i][4])
							hello['hold'] = list()
							hello['hold'].append(ans_final[i][3])
							hello['srtt'] = list()
							hello['srtt'].append(ans_final[i][5])
							hello['rto'] = list()
							hello['rto'].append(ans_final[i][6])
							hello['iteration'] = list()
							hello['iteration'].append(iter)
							if neigh in devicedict.gennodedict['eigrp_neigh']:
								devicedict.gennodedict['eigrp_neigh'][neigh]['iteration'].append(iter)
								devicedict.gennodedict['eigrp_neigh'][neigh]['hold'].append(ans_final[i][3])
								devicedict.gennodedict['eigrp_neigh'][neigh]['uptime'].append(ans_final[i][4])
								devicedict.gennodedict['eigrp_neigh'][neigh]['srtt'].append(ans_final[i][5])
								devicedict.gennodedict['eigrp_neigh'][neigh]['rto'].append(ans_final[i][6])
								devicedict.gennodedict['eigrp_neigh'][neigh]['uptime']=hello['uptime']
				
							else:
								devicedict.gennodedict['eigrp_neigh'][neigh]=dict()
								devicedict.gennodedict['eigrp_neigh'][neigh]=hello
					time.sleep(1)
			print("\nFINAL DICT:\n")	
			print(devicedict.gennodedict['eigrp_neigh'])



	if flag1==1:
		print("bgp there")
		devicedict.gennodedict['bgp_neigh']=dict()
		devicedict.gennodedict['bgp_neigh']['Number_of_neigh']='Number of neighbors constant'
		three=[]
		neigh_wise=dict()
		all_bgp_neigh=set()
		for rot in range(3):
			ret=ssh.send_command("sh ip bgp summary",use_textfsm=True)
			#print(ret)
			fhand.write("Show ip :bgp summary\n")
			fhand.write(str(ret))
			fhand.write("\n\n")
			three.append(ret)
			for move in range(0,len(ret)):
				if ret[move]['bgp_neigh'] not in all_bgp_neigh:
					all_bgp_neigh.add(ret[move]['bgp_neigh'])
					neigh_wise[ret[move]['bgp_neigh']]=list()
				neigh_wise[ret[move]['bgp_neigh']].append(ret[move])
			time.sleep(1)

		if len(three[0])!=len(three[1]) and len(three[1])!=len(three(2)):
			#number of neighbors not constant
			devicedict.gennodedict['bgp_neigh']['Number_of_neigh']='Number of neighbors not constant'
		for i in neigh_wise.keys():
			print(neigh_wise[i])
			print("\n")

		for neigh in all_bgp_neigh:
			len_list=len(neigh_wise[neigh])
			a=neigh_wise[neigh][0]
			b=neigh_wise[neigh][1]
			c=neigh_wise[neigh][2]
			c['condition']=''
			c['condition']='perfect'
			concheck=1
			if a['state_pfxrcd']!=b['state_pfxrcd'] and b['state_pfxrcd']!=c['state_pfxrcd']:
				if concheck==1:
					concheck=0
					c['condition']=''
				c['condition']+='Number of routes exchanged is changing. '  
	
			if a['state_pfxrcd']=='Idle (Admin)' or b['state_pfxrcd']=='Idle (Admin)' or c['state_pfxrcd']=='Idle (Admin)':
				if concheck==1:
					concheck=0
					c['condition']=''
				c['condition']+='Neighbor in Idle (Admin) state. Check if it is shutdown. '

			if a['state_pfxrcd'].isdigit()==False or b	        ['state_pfxrcd'].isdigit()==False or c['state_pfxrcd'].isdigit()==False :
				if concheck==1:
					concheck=0
					c['condition']=''
				c['condition']+='Routes not being exchanged. '
		
			if a['updown']=='never' or b['updown']=='never' or c['updown']=='never':
				c['condition']+='. Neighborship not established properly. '
			if re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}$',a['updown']):
				if not(re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}$',b['updown'])) or not(re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}$',c['updown'])):
					if concheck==1:
						concheck=0
						c['condition']=''
					c['condition']+='Neighborship flapping. '

				else:
					at1=int(a['updown'][:2])*60*60+int(a['updown'][3:5])*60+int(a['updown'][6:])
					bt1=int(b['updown'][:2])*60*60+int(b['updown'][3:5])*60+int(b['updown'][6:])
					ct1=int(c['updown'][:2])*60*60+int(c['updown'][3:5])*60+int(c['updown'][6:])
					if not(at1<bt1) or not(bt1<ct1):
						if concheck==1:
							concheck=0
							c['condition']=''
						c['condition']+='Neighborship Flapping. '
			
			if re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}$',c['updown']):
				ct1=int(a['updown'][:2])*60*60+int(a['updown'][3:5])*60+int(a['updown'][6:])
				if ct1<3600:
					if concheck==1:
						concheck=0
						c['condition']=''
					c['condition']+='Neighbor uptime less than an hour. '
			print("\n\n")    
			print(c)
			devicedict.gennodedict['bgp_neigh'][c['bgp_neigh']]=dict()
			devicedict.gennodedict['bgp_neigh'][c['bgp_neigh']]=c

	return devicedict