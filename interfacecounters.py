from collections import defaultdict
def check_interfacecounters(ssh,nme,version,fhand,devicedict):
    print("For show interface counters")
	
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
			int_d[xint] = int_d[xint][:3] 
		
	devicedict.gennodedict['interface_counters_errors']=m
	return devicedict