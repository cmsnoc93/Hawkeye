def check_cpu(ssh,nme,version,fhand,devicedict):
   

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
                #ssh=ConnectHandler(device_type=version,host=devicedict.sship,username="rit",password="CMSnoc$1234")
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
                #ssh=ConnectHandler(device_type=version,host=devicedict.sship,username="rit",password="CMSnoc$1234")
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

    return devicedict