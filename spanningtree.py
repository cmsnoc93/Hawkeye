def check_spanningtree(ssh,nme,version,fhand,devicedict):
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

    return devicedict