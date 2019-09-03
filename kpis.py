def fetchKPI(ssh,nme,path_no,devicedict):
				# print(context)
				# print(context.app_context())
				# print(context.app_context().g)
				# print(str(context.app_context().g))
				# print(context.app_context().g.dictofobj)
				# with app.test_request_context():
					
					# SHOW PROC CPU
					fname=nme+".txt"
					fhand=open(fname,'w')

					version = devicedict.gennodedict['version']['soft_ver']
					fhand.write("<!doctype html><html><head> <title>"+nme+"</title></style></head><body>")
					fhand.write("Version "+version+"\n\n")
					if version != 'cisco_nxos':	    
						boo=True
						while boo:
							try:
								ret=ssh.send_command("sh proc cpu | ex 0.0",use_textfsm=True)
								print(ret)
								boo=False
							except Exception as e: 
								print("9 Exception Raised , Trying again",e)
								boo=True
								ssh=ConnectHandler(device_type=version,host=devicedict.sship,username="rit",password="CMSnoc$1234")
								continue
							if not(isinstance(ret,list)):
								boo=True
								print("9 return from sh proc cpu not proper, trying again",nme,ssh.device_type)
							else:
								boo=False	            
						fhand.write("Show proc cpu | ex 0.0\n")
						fhand.write(str(ret))
						fhand.write("\n\n")
						ct1=0
						for line in ret:

							if ct1==0:
								cpu={}
								if 'cpu_5_sec' in line.keys():
									cpu['cpu_5_sec']=line['cpu_5_sec']
								if 'cpu_1_min' in line.keys():
									cpu['cpu_1_min']=line['cpu_1_min']
								if 'cpu_5_min' in line.keys():
									cpu['cpu_5_min']=line['cpu_5_min']
								devicedict.gennodedict['CPU']=cpu                
								
							combine={}
							if 'process' in line.keys():
								combine['process']=line['process']
							if 'proc_5_sec' in line.keys():
								combine['proc_5_sec']=line['proc_5_sec']
							if 'proc_1_min' in line.keys():
								combine['proc_1_min']=line['proc_1_min']
							if 'proc_5_min' in line.keys():
								combine['proc_5_min']=line['proc_5_min']
							devicedict.gennodedict[line['pid']]=combine      
							ct1+=1
					#NXOS SH PROC CPU
					if version == 'cisco_nxos':	    
						boo=True
						while boo:
							try:
								ret=ssh.send_command("sh proc cpu | ex 0.0",use_textfsm=True)
								print(ret)
								boo=False
							except Exception as e: 
								print("9 Exception Raised , Trying again",e)
								boo=True
								ssh=ConnectHandler(device_type=version,host=devicedict.sship,username="rit",password="CMSnoc$1234")
								continue
							if not(isinstance(ret,list)):
								boo=True
								print("9 return from sh proc cpu not proper, trying again",nme,ssh.device_type)
							else:
								boo=False	            
						
						print("NEXUS CPU: ", ret)
						fhand.write("Show proc cpu | ex 0.0 \n")
						fhand.write(str(ret))
						fhand.write("\n\n")
						ker_flag=0
						for line in ret:

							cpu={}
							if line['kernel']!='':
								cpu['user']=line['user']
								cpu['kernel']=line['kernel']
								cpu['idle']=line['idle']
								devicedict.gennodedict['CPU']=cpu   
								ker_flag=1             
							else:
								combine={}
								if 'process' in line.keys():
									combine['process']=line['process']
								if 'proc_1_sec' in line.keys():
									combine['proc_1_sec']=line['proc_1_sec']
								devicedict.gennodedict[line['pid']]=combine 
						if ker_flag==0:
							ret=ssh.send_command("show proc cpu | inc kernel") 
							ret=ret.split()
							fhand.write("Show proc cpu | inc kernel\n")
							fhand.write(str(ret))
							print(ret)
							fhand.write("\n\n")
							cpu={}
							cpu['kernel']=ret[ret.index('kernel,')-1][:-1]
							cpu['user']=ret[ret.index('user,')-1][:-1]
							cpu['idle']=ret[ret.index('idle')-1][:-1]
							devicedict.gennodedict['CPU']=cpu
					# SHOW IP ROUTE
					version = devicedict.gennodedict['version']['soft_ver']
					print("VERSION ",version)
					if version=='cisco_nxos':
						ret=ssh.send_command("sh ip route | inc 00:",use_textfsm=True)
						print(ret)
						fhand.write("Show ip route | i 00: \n")
						fhand.write(str(ret))
						fhand.write("\n\n")
						make_dict=dict()
						ct1=1
						for rou in ret:
							print(rou)
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
								
							
				#-----------------------------------------Harshad------------------------------------------------------------------------------------------
						
					# SHOW IP PROTOCOLS
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


							
							
						


				#----------------------------------------------------------------------------------------------------------------------------------------------


				#------------------------------------------Neeraj-----------------------------------------------------------------------------------------------
					#version = devicedict.gennodedict['version']['soft_ver']


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
								break;
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


				#---------------------------------------------------------------------------------------------------------------------------------------
				#---------------------------------------------------ARAVIND-----------------------------------------------------------------------------


					map_return = {}
					
					print("For Spanning Tree KPI")
					#print(devicedict.gennodedict['version']['hardware'])
					output_span=''
					#if devicedict.gennodedict['version']['hardware']=='3725':
					if True:        
						boo=True
						while boo:
							try:
								output_span= ssh.send_command("sh spanning-tree active")
								boo=False
							except:
								boo=True
								print("9-6 Exception Raised in show spanning tree")
							if not output_span:
								print(" 9-6 Return from show spanning tree is null. Trying again ")
								boo=True
							elif not(isinstance(output_span,str)):
								boo=True
								print(" 9-6 Return from show spanning tree is not a string. Trying again ")
								
							elif len(output_span.split())<4:
								boo=True
								print(" 9-6 Return from show spanning tree is not proper. Trying again")
							else:
								boo=False
						fhand.write("Show spanning-tree active\n")
						fhand.write(output_span)
						fhand.write("\n\n")
						l=output_span.split('\n')
						print("Spanning LIST")
						print(l)
						flag = 0
						p = 12
						m1={}
						for k in range(len(l)-6):
							if (k == p):
								print(" k ")
								print(k)
								print(" p ")
								print(p)
								print(l[k])
								print(l[k + 6])
								m1[l[k]] = l[k + 6]
								p += 9
						p = 12
						#time.sleep(1)
						for lo in range(0, 2):
							for k in range(len(l)-6):
								if (k == p):
									print(" k ")
									print(k)
									print(" p ")
									print(p)
									# print(l[k])
									# print(l[k+6])
									if (m1[l[k]] != l[k + 6]):
										map_return[l[k]] = l[k + 6]
										print(l[k] + "\n" + l[k + 6])
										flag = 1
									else:
										print("No change Observed")
										flag = 0
									p += 9
							p = 12
							time.sleep(1)
						if (flag == 0):
							print("No Changes in the Past 1 minute")
						flag = 0
						print('\n\n\n')
					devicedict.gennodedict['spanning_tree']=map_return
					







					print("For show interface counters")
					"""
					#print(devicedict.gennodedict['version']['hardware'])
					Int_count={}
					print(nme," ",devicedict.gennodedict['version']['soft_ver'])
					if devicedict.gennodedict['version']['soft_ver']=='cisco_ios':
					#if ios_ver=='cisco_ios':	     
						boo=True
						while boo:
							try:
								command = ssh.send_command("sh int counters error | ex 0")
								boo=False
							except:
								boo=True
								print("9-7 Exception handled - sh int counters error, Trying again")
							print("Return from show int counters error")
							print(command)
						fhand.write("Show int counters error | ex 0\n")
						fhand.write(command)
						fhand.write("\n\n")
							
						if not(command):
							print("Sorry empty")
						else:           
							s = 'Port      Single-Col  Multi-Col   Late-Col  Excess-Col  Carri-Sen      Runts     Giants '
							m = defaultdict(list)
							count = -2
							m1 = defaultdict(list)
							for j in range(0,3):
								ret1 = ssh .send_command("sh interface counters errors")
								l2 = ret1.split("\n")
								for i in l2[2:]:
										if('Port' not in i):
											count += 1
											list1 = i.split(' ')
											while ("" in list1):
												list1.remove("")
											if(len(list1)!=0):
												m[list1[0]].append(list1[1: ])
							# print(i)
										elif('Port' in i):
											break
							count = int(count/3)
							count+=3
							for j in range(0,3):
								for i in l2[count+1 : ]:
										list1 = i.split(' ')
										while ("" in list1):
											list1.remove("")
							#print(list1)
										if(len(list1)!=0):
											m1[list1[0]].append(list1[1: ])

							for x in m.keys():
								m[x] = m[x] + m1[x]
							print(m)
							for x in m.keys():
								k = int(len(m[x]) / 2)
								for y in range(0, k):
									m[x][y] = m[x][y] + m[x][y + 3]
								m[x] = m[x][:3]
							print("The errors are \n")
							print(m)

					if devicedict.gennodedict['version']['soft_ver']=='cisco_nxos':     
						boo=True
						while boo:
							try:
								command = ssh.send_command("sh int counters error | ex 0")
								boo=False
							except:
								boo=True
								print("9-7 Exception handled - sh int counters error, Trying again")
							print("Return from show int counters error")
							print(command)
						fhand.write("Show int counters error | ex 0\n")
						fhand.write(command)
						fhand.write("\n\n")
							
						if not(command):
							print("Sorry empty")
						else:           
							s = 'Port      Single-Col   Multi-Col    Late-Col   Exces-Col   Carri-Sen       Runts'
							s1 = 'Port          Giants  SQETest-Er Deferred-Tx IntMacTx-Er IntMacRx-Er  Symbol-Err'
							s2 = 'mgmt0             --          --          --          --          --          --'
							int_d = defaultdict(list)	
							int_d_1 = defaultdict(list)
							int_d_2 = defaultdict(list)
							count = -4

							for j in range(0,3):
								ret1 = ssh.send_command("sh int counters error")
								list_1 = ret1.split("\n")
								for i in list_1[4:]:
									if ('Port' not in i):
										count += 1
										list1 = i.split(' ')
										while ("" in list1):
											list1.remove("")
											#print(list1)
										if (len(list1) != 0):
											int_d[list1[0]].append(list1[1:])
									elif ('Port' in i):
										break
				#print(m)
							count = int(count / 3)
							count += 8
							k=count
			#print(list_1[count])
							list1 = []
							for j in range(0,3):
								for i in list_1[k:]:
									if 'Port' not in i:
										count += 1
										list1 = i.split(' ')
										while "" in list1:
											list1.remove("")
									if len(list1) != 0:
										int_d_1[list1[0]].append(list1[1:])
									elif 'Port' in i:
										break
			#print(m1)
							count = int(count / 3)
							count+=51
			#print(list_1[count])
							k1 = count
			#print(list_1[k1:])
							list1= []
							for j in range(0, 3):
								for i in list_1[k1:]:
									if 'mgmt0' not in i:
										list1 = i.split(' ')
										while ("" in list1):
											list1.remove("")
										if (len(list1) != 0):
											int_d_2[list1[0]].append(list1[1:])
									elif 'mgmt0' in i:
										break

			#print(m2)

							for x in int_d.keys():
								int_d[x] = int_d[x] + int_d_1[x]
								int_d[x] = int_d[x] + int_d_2[x]
								print("Map is", int_d)
								if 'mgmt0' in int_d:
									int_d.pop('mgmt0')
								if '--------------------------------------------------------------------------------' in int_d:
									int_d.pop('--------------------------------------------------------------------------------')
				#print(m)
								print(int_d)
							for xint in int_d.keys():
							if xint != 'mgmt0':
								k = int(len(int_d[xint]) / 3)
								print("K is", k)
								for yint in range(0, k):
								lco = yint+3
								int_d[xint][yint] = int_d[xint][yint] + int_d[xint][lco]
								#print(m)
								if k==3:
								for yint in range(0,k):
									lco=lco+1
									print(lco,xint)
								#print(int_d[xint])
								#print(int_d)
									int_d[xint][yint] = int_d[xint][yint] + int_d[xint][lco]
							int_d[xint] = int_d[xint][:3] """
					m = {}	
					devicedict.gennodedict['interface_counters_errors']=m
















				#---------------------------------------------------------------------------------------------------------------------------------------------------



					# SHOW INTERFACES
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