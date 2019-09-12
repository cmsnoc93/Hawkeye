import paramiko, re
from netmiko import ConnectHandler, SSHDetect
from hawkutils import _ping_to, router, expand_name
from flask import g


def tracenext(connec,destin,os,numb):
    cross_prov_ip='no'
    retu=connec.send_command("traceroute "+destin)
    retu=retu.split('\n')
    for line in retu:
        line=line.split()
        print(line)
        if len(line)>1 and line[0]==numb: #number can be changed
            print('Next hop ip beyond SP is '+line[1])
            cross_prov_ip=line[1]

    return cross_prov_ip

def interf_desc(os,interface_out):
    #Nexus not included
    sp='no'
    if os!='cisco_nxos':
        ret=ssh.send_command("show interfaces description",use_textfsm=True)
        for line in ret:
            if line['port']==interface_out or line['port']==expand_name(interface_out):
                if line['descrip']=='Service Provider':
                    sp='yes'
            break
    return sp

def get_path(src,dst):
    src=src
    dst=dst	
    def_gw='10.8.14.14'
    #default gateway hard coded as of now
    arr=[]
    count=0

    setofnames=set()
    dictofnames={}

    ssh_failure_any=False
    name=''
    s={src}
    now=src
    honame=set()
    exit=dict()
    entry=dict()
    entryrev=dict()
    ls=[]
    ls.append(now)
    extract=set()
    p=''
    boo=True

    ssh_series=list()
    
    ping_stat=dict()
    ping_stat['terminate']='false'
    ping_stat['ping_failure']='false'
    ping_stat['ssh_failure']='false'
    ping_stat['cloud']=dict()
    ping_stat['exit_to_cloud']=False
    ping_stat['ssh_err_ip']=list()



    ping_stat['source']=_ping_to(src)
    if ping_stat['source']!='perfect':
        ping_stat['dg']=_ping_to(def_gw)
        ping_stat['terminate']='true'
        ping_stat['ping_failure']='true'
        return entry,exit,entryrev,setofnames,ping_stat
    else:
        ping_stat['dg']='perfect'

    while(len(s)>0):
        now=ls[0]
        rem=paramiko.SSHClient()
        rem.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            rem.connect(now,port=22, username='rit',password='CMSnoc$1234')
            
            print ("SSH connection established for getting the version - ",now)
            stdin,stdout,stderr=rem.exec_command("show version")
            
        except Exception as e:
            print("Error in ssh connection, Trying again. Error - ",e)
            ping_stat['terminate']='true'
            ping_stat['ssh_failure']='true'
            ping_stat['ssh_err_ip'].append(now)
            ssh_failure_any=True
            s.remove(now)
            ls.remove(now)
            continue
            #return exit,entryrev,g.intojson,ping_stat
            


        output=stdout.readlines()
        output='\n'.join(output)
        k9=output.replace('\n',' ')
        k9=k9.split()
        a=k9.index('Cisco')
        ios_ver=''
        verdict={}
        if (k9[a+1]=='IOS'):
            if (k9[a+2]=='XE'):
                ios_ver='cisco_xe'
            else:
                ios_ver='cisco_ios'
        else:
            ios_ver='cisco_nxos'
        
        print(ios_ver)


        verdict['soft_ver']=ios_ver

        if ios_ver=='cisco_nxos':
            if 'BIOS:' in k9 and 'kickstart:' in k9:
                var=k9.index('BIOS:')
                var3=k9.index('kickstart:')
                verdict['version']="BIOS: "+k9[var+2]+" Kickstart: "+k9[var3+2]
            if 'uptime' in k9 and 'second(s)' in k9:
                var=k9.index('uptime')
                var2=k9.index('second(s)')
                verdict['uptime']=' '.join(k9[var+2:var2+1])
            if 'Hardware' in k9:
                var=k9.index('Hardware')
                verdict['hardware']=' '.join(k9[var+1:var+3])
            if 'Reason:' in k9:
                var=k9.index('Reason:')
                verdict['reload_reason']=k9[var+1]
        
        elif ios_ver=='cisco_xe':
            if 'weeks,' in k9 and 'minutes' in k9:
                var=k9.index('weeks,')
                var2=k9.index('minutes')
                verdict['uptime']=' '.join(k9[var-1:var2+1])
            if 'Last' in k9 and 'This' in k9:
                var=k9.index('Last')
                var2=k9.index('This')
                verdict['reload_reason']=' '.join(k9[var+3:var2])
            if 'Version' in k9:
                var=k9.index('Version')
        
                verdict['version']=k9[var+1]
        else:
            if 'Version' in k9:
                var=k9.index('Version')
                verdict['version']=' '.join(k9[var+1][:-1])
            if 'Software,' in k9:
                var=k9.index('Software,')
                verdict['hardware']=k9[var+1]  
            if 'uptime' in k9 and 'minutes' in k9:
                var=k9.index('uptime')
                var2=k9.index('minutes')
                verdict['uptime']=' '.join(k9[var+2:var2+1]) 
            if 'reason:' in k9 and 'This' in k9:           
                var=k9.index('reason:')
                var2=k9.index('This')
                verdict['reload_reason']=' '.join(k9[var+1:var2])

        print(verdict)
        rem.close()

        boo=True
        
        try:
            ssh= ConnectHandler(device_type=ios_ver,host=now,username="rit",password="CMSnoc$1234") 
        except Exception as e:
            boo=True
            print(" Connection error ",e)
            ping_stat['terminate']='true'
            ping_stat['ssh_failure']='true'
            ping_stat['ssh_err_ip'].append(now)
            ssh_failure_any=True
            s.remove(now)
            ls.remove(now)
            continue
            #return exit,entryrev,g.intojson,ping_stat

        #ret=ssh.send_command("en")
        boo=True
        while boo:
            try: 
                name=ssh.find_prompt()
                boo=False
            except Exception as e:
                print(str(e))
                print("Trying again")
                boo=True
            if not(re.match("^[A-Z]{3}-{2}[A-Z]{2}[0-9]{2}#{1}$",name)):
                boo=True
                print(" Name Received Incorrect- Trying again "+name)
        
        name=name[:-1]


        if name not in setofnames:
            setofnames.add(name)
            dictofnames[name]=count
            k=router(name)
            arr.append(k)
            g.dictofobj[name]=k
            g.dictofobj[name].addconnect(ssh)
            g.dictofobj[name].addsship(now)
            g.dictofobj[name].addsshpass(True)
            count+=1
            
        g.dictofobj[name].gennodedict['version']=verdict
        print(name)
        honame.add(name)
        print("dict of names ")
        print(dictofnames)
        t3=0

        if now==src:
            ret=ssh.send_command('ping '+dst)
            ret=ret.split()
            print(ret)
            if ios_ver!='cisco_nxos':
                ret_loc=ret.index('rate')
                succ_perc=int(ret[ret_loc+2])
                if succ_perc>=80:
                    ping_stat['dest']='perfect'
                else:
                    ping_stat['dest']='Not reachable'
                    ping_stat['terminate']='true'
                    ping_stat['ping_failure']='true'
                    return entry,exit,entryrev,g.intojson,ping_stat
            else:
                ret_loc=ret.index('received,')
                succ_num=int(ret[ret_loc-2])
                if succ_num>=4:
                    ping_stat['dest']='perfect'
                else:
                    ping_stat['dest']='Not reachable'
                    ping_stat['terminate']='true'
                    ping_stat['ping_failure']='true'
                    return entry,exit,entryrev,g.intojson,ping_stat
            ret=ssh.send_command('sh ip int brief | inc '+src)
            print(" SOURCE INTERFACE "+ ret)
            source_int=ret.split()[0]
            g.dictofobj[name].adddictip(source_int,src)
        
        if ios_ver=='cisco_nxos':
            ret=ssh.send_command("sh ip route "+dst)
            print(" return from sh ip route | inc known via ")
            ret=ret.split('\n')[6:]
            print(ret)
            prot='connected",'

            if 'attached' in ret[0]:
                print('connected",')
                prot='connected",'
            else:
                t3=0
            for line in ret:
                line=line.split()    
                for word in line:
                    #print(word)
                    if re.match('^eigrp*',word):
                        print("eigrp")
                        prot='eigrp'
                        t3=1
                        break
                if t3==1:
                    break
#bgp condition not included

        
        else:
            
        
            boo2=True
            while boo2:
        
                boo=True
                while boo:
                    try:
                        ret=ssh.send_command("sh ip route "+dst+" | include Known via")
                        boo=False
                    except Exception as e:
                        boo=True
                        print("1 Exception Handled- Trying again")
                    print(" return from sh ip route | inc known via ")
                    print(ret)
                    if not ret:
                        print("1 Trying again")
                        boo=True
                    elif isinstance(ret,list):
                        print("1 Return from sh ip route is a list, trying again")
                        boo=True
                    elif len(ret.split())>=3:
                        boo=False
                    else:
                        print("1 Trying Again sh ip route")
                        boo=True
                print(" Name "+name+" show ip route | i known via")
                print(ret)
                ret=ret.split()
                prot=ret[2][1:]
                print("PROT- "+prot)
                if prot!='bgp' and prot !='connected",' and prot!='eigrp':
                    boo2=True
                    print(" Protocol received isn't correct. Trying Again ")
                else:
                    boo2=False
                
        
        
        if prot=='bgp':
            dst1=dst
            fl=0
            print("Prot BGP")
            while fl!=2:
                boo=True
                while boo:
                    try:
                        ret=ssh.send_command("sh ip route "+dst1)
                        boo=False
                    except:
                        boo=True
                        print("2 Exception Handled- Trying again")

                    if not ret:
                        boo=True
                        print("2 Trying again")
                    elif isinstance(ret,list):
                        print("2 Return from sh ip route is a list, trying again")
                        boo=True
                    elif len(ret.split())>3:
                        boo=False
                    else:
                        boo=True
                        print("2 Trying again")
                print("\tBGP- sh ip route for dst "+dst1)
                print(ret)
                ret=ret.split("\n")
                fl=0
                for i in ret:
                    i=i.split()
                    print("splitting ret")
                    print(i)
                    if i[0]=='*':
                        nxt=i[1]
                        if nxt=='directly':
                            x=i.index('via')
                            hop=i[x+1]
                            fl=2
                            break
                        elif re.match('^(?:[0-9]{1,3}\.){3}([0-9]{1,3})',nxt):
                            dst1=nxt
                            if nxt[-1]==',':
                                dst1=nxt[:-1]

                            fl=1
                            break
            print("Name "+name+" BGP: next hop "+dst1+" exit interface "+hop)
            extract.add(dst1)
 
            desc_response=interf_desc(ios_ver,hop)
            
            if desc_response=='yes':
                cross_ip=tracenext(ssh,dst,ios_ver,2)
                ping_stat['cloud']['entry']=dst1
                ping_stat['cloud']['exit_to']=cross_ip
                ping_stat['exit_to_cloud']=True
                s.add(cross_ip)
                ls.append(cross_ip)

            else:
                s.add(dst1)
                ls.append(dst1)



            p=''
            p=hop+' '+dst1
            if name not in exit.keys():
                exit[name]=set()
            exit[name].add(p)
            boo=True
            while boo:
                try:    
                    ret=ssh.send_command("sh ip int brief | include "+hop)
                    boo=False
                except:
                    print("3 Exception Handled- Trying again")
                    boo=True
                if not ret:
                    boo=True
                elif isinstance(ret,list):
                    print("3 Return from sh ip int brief is a list, trying again")
                    boo=True
                elif len(ret.split())<6:
                    boo=True
                else:
                    boo=False
                    
            ip=ret.split()[1]
            ctobj=dictofnames[name]
            arr[ctobj].addexit(p)
            g.dictofobj[name].adddictip(hop,ip)

            p=''
                
        elif prot=='connected",':
            if ios_ver=='cisco_nxos':
                ret=ssh.send_command("sh ip route "+dst)
                print(" return from shhh ip route | inc known via ")

                ret=ret.split('\n')
                for mk in ret:
                    if 'ubest' in mk:
                        ret=ret[ret.index(mk):]
                        break
                print(ret)
                ret=ret[1].split()
                print(ret)
                posn=ret.index('*via')
                print(posn)
                exit_int=ret[posn+2][:-1]
                print(exit_int)
                ret=ssh.send_command("sh ip int brief | include "+exit_int)
                if ret == '':
                    print(exit_int + "inside null")
                    exit_int = 'Ethernet'+exit_int[-3:]
                    print(exit_int)
                    ret=ssh.send_command("sh ip int brief | include "+exit_int)
                ret=ret.split()
                print(ret)
                exit_int_ip=ret[1]
                print(exit_int_ip)
                p=''
                p=exit_int+' directly'

                if name not in exit.keys():
                    exit[name]=set()
                exit[name].add(p)
                print(" Name "+name+" is connected to dst via "+p)

                ctobj=dictofnames[name]
                arr[ctobj].addexit(p)
                g.dictofobj[name].adddictip(exit_int,exit_int_ip)

                p=''

            else:


                boo=True
                while boo:
                    try:
                        ret=ssh.send_command("sh ip route "+dst+" | include directly")
                        boo=False
                    except:
                        boo=True
                        print("4 Exception Handled- Trying again")
                    print(" Return from sh ip route dst i directly")
                    print(ret)
                    if not ret:
                        boo=True
                        print("4 Return from show ip route dst is null, Trying again")
                
                    elif isinstance(ret,list):
                        print("4 Return from sh ip route directly is a list, trying again")
                        boo=True
                    elif len(ret.split())>3:
                        boo=False
                    else:
                        print("4 Trying again")
                        boo=True
            
                print("Connected route- show ip route| i directly ")
                print(ret)
                ret=ret.split()
                p=''
                x=ret.index('via')
                p=ret[x+1]
                hop=ret[x+1]
                p=p+' directly'
                if name not in exit.keys():
                    exit[name]=set()
                exit[name].add(p)
                print(" Name "+name+" is connected to dst via "+p)

                ctobj=dictofnames[name]
                arr[ctobj].addexit(p)
                boo=True
                while boo:
                    try:    
                        ret=ssh.send_command("sh ip int brief | include "+hop)
                        boo=False
                    except:
                        print("5 Exception Handled- Trying again")
                        boo=True
                    if not ret:
                        boo=True
                    elif isinstance(ret,list):
                        print("5 Return from sh ip int brief is a list, trying again")
                        boo=True
                    elif len(ret.split())<6:
                        boo=True
                    else:
                        boo=False
                
                    
                ip=ret.split()[1]

                g.dictofobj[name].adddictip(hop,ip)

                p=''
    
        else:
            if ios_ver=='cisco_nxos':

                ret=ssh.send_command("sh ip route "+dst+" | include via")
                #ret=ret.split('\n')[6:]
                print(ret)
                #posn=ret.index('*via')
                #next_hop_ip=
                ret=ret.split('\n')
                for line in ret:
                    line=line.split()
                    print(line)
                    if '*via' in line:
                        via_pos=line.index('*via')
                        next_hop_ip=line[via_pos+1][:-1]
                        exit_int=line[via_pos+2][:-1]
                        ret2=ssh.send_command("sh ip int brief | include "+exit_int)
                        if ret2 == '':
                            print(exit_int + "inside null")
                            exit_int = 'Ethernet'+exit_int[-3:]
                            print(exit_int)
                            ret2=ssh.send_command("sh ip int brief | include "+exit_int)
                            print("[[[[["+ret2)
                        ret2=ret2.split()
                        print(ret2)
                        exit_int_ip=ret2[1]
                        print(next_hop_ip+"   "+exit_int+"  "+exit_int_ip)


                        if next_hop_ip not in extract:
                            extract.add(next_hop_ip)
                            desc_response=interf_desc(ios_ver,exit_int)
                            if desc_response=='yes':
                                cross_ip=tracenext(ssh,dst,ios_ver,2)
                                ping_stat['cloud']['entry']=dst1
                                ping_stat['exit_to_cloud']=True
                                ping_stat['cloud']['exit_to']=cross_ip
                                s.add(cross_ip)
                                ls.append(cross_ip)

                            else:
                                s.add(next_hop_ip)
                                ls.append(next_hop_ip)
                            
                            p=''  
                            
                            p=exit_int+' '+next_hop_ip
                            if name not in exit.keys():
                                exit[name]=set()
                
                            exit[name].add(p)

                            ctobj=dictofnames[name]
                            #print("ctobj "+ctobj)
                            arr[ctobj].addexit(p)
                            g.dictofobj[name].adddictip(exit_int,exit_int_ip)

                            p=''	                        

            else:


                boo=True
                while boo:
                    try:
                        ret=ssh.send_command("sh ip route "+dst+" | include via")
                        boo=False
                    except:
                        boo=True
                        print("6 Exception Handled- Trying again")
                    print(" Return from sh ip route")
                    print(ret)
                    if not ret:
                        boo=True
                        print("6 Trying again")
                
                    elif isinstance(ret,list):
                        print("6 Return from sh ip route is a list, trying again")
                        boo=True
                    elif len(ret.split())>3:
                        boo=False
                    else:
                        print("6 Trying again")
                        boo=True
                print("output from sh ip route | inc via ")
                print(ret)
                print("Splitting")
                ret=ret.split('\n')
                for i in ret:
                    i=i.split()
                    print(i)
                    t=0
                    for j in i:
                    #print(j)
                        if re.match('^(?:[0-9]{1,3}\.){3}([0-9]{1,3})',j):
                            print("extract- "+j[:-1])
                            j=j[:-1] 
                                
                            num=i.index('via')
                            p=i[num+1]
                            hop=i[num+1]
                            p=p+' '+j
                            if j not in extract:
                                extract.add(j)

                                desc_response=interf_desc(ios_ver,hop)
                                if desc_response=='yes':
                                    cross_ip=tracenext(ssh,dst,ios_ver,2)
                                    ping_stat['cloud']['entry']=dst1
                                    ping_stat['exit_to_cloud']=True
                                    ping_stat['cloud']['exit_to']=cross_ip
                                    s.add(cross_ip)
                                    ls.append(cross_ip)                             
                                else:
                                    s.add(j)
                                    ls.append(j) 

                            if name not in exit.keys():
                                exit[name]=set()
                
                            exit[name].add(p)

                            ctobj=dictofnames[name]
                            #print("ctobj "+ctobj)
                            arr[ctobj].addexit(p)
                            print("hop ",hop)
                            boo=True
                            ret1=""
                            while boo:
                                try:    
                                    ret1=ssh.send_command("sh ip int brief | include "+hop)
                                    boo=False
                                except:
                                    print("6-2 Exception Handled- Trying again")
                                    boo=True
                                print(" Return ")
                                print(ret1)
                                print(len(ret1.split()))
                                #print(ret1.split()[0])
                                if not ret1:
                                    boo=True
                                elif isinstance(ret1,list):
                                    print("6-2 Return from sh ip int brief is a list, trying again")
                                    boo=True
                                elif len(ret1.split())<5:
                                    boo=True
                                else:
                                    boo=False
                        
                            ip=ret1.split()[1]
                            g.dictofobj[name].adddictip(hop,ip)

                            p=''
                            break
        extract.clear()
        s.remove(now)
        ls.remove(now)
    
        if now!=src:
            if ios_ver=='cisco_nxos':
    
                ret=ssh.send_command('sh ip int brief | include '+now)
                ret=ret.split()
                entry_int=ret[0]
                print("entry interface "+entry_int)

    
                if name not in entry.keys():
                    entry[name]=set()
                p=''
                
                p=entry_int+' '+now
                entry[name].add(p)

                ctobj=dictofnames[name]
                arr[ctobj].addentry(p)
                g.dictofobj[name].adddictip(entry_int,now)
            

                entryrev[now]=set()
                p=''
                p=name+' '+entry_int
                entryrev[now].add(p)

            else:

                boo=True
                while boo:
                    try:    
                        ret=ssh.send_command("sh ip int brief | include "+now)
                        boo=False
                    except:
                        print("7  Exception Handled- Trying again")
                        boo=True
                    print(" return from sh ip int brief | inc dest at dest ")
                    print(ret)
                    print(len(ret.split()))
                    if not ret:
                        print("7 null")
                        boo=True
                    elif isinstance(ret,list):
                        print("7 Return from sh ip route is a list, trying again")
                        boo=True
                    elif len(ret.split())<6:
                        boo=True
                        print("7 Trying Again")
                    else:
                        boo=False
                print(" Name "+name+" sh ip int brief | include "+now)
                print(ret)
                ret=ret.split()
    
                if name not in entry.keys():
                    entry[name]=set()
                p=''
                p=ret[0]
                hop=ret[0]
                ip=now
                p=p+' '+now
                entry[name].add(p)

                ctobj=dictofnames[name]
                arr[ctobj].addentry(p)
                g.dictofobj[name].adddictip(hop,ip)
            

                entryrev[now]=set()
                p=''
                p=name+' '+ret[0]
                entryrev[now].add(p)
        

    
    
    rem=paramiko.SSHClient()
    rem.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    boo=True
    try:
        rem.connect(dst,port=22, username='rit',password='CMSnoc$1234')
        boo=False
        print ("SSH connection established for getting the version - ",now)
        stdin,stdout,stderr=rem.exec_command("show version")
    except Exception as e:
        print("Error in ssh connection, Trying again. Error - ",e) 
        boo=True
        ping_stat['terminate']='true'
        ping_stat['ssh_failure']='true'
        ping_stat['ssh_err_ip'].append(dst)
        ssh_failure_any=True

        #return exit,entryrev,g.intojson,ping_stat   
    if ssh_failure_any==True:
        return entry,exit,entryrev,setofnames,ping_stat 
    output=stdout.readlines()
    print(output)
    output='\n'.join(output)
    k9=output.replace('\n',' ')
    print("\n\n\n\n")
    print(k9)
    k9=k9.split()
    print("\n\n\n\n")
    print(k9)
    a=k9.index('Cisco')
    #print(a)
    #print(k9[a+1])
    ios_ver=''
    verdict={}
    if (k9[a+1]=='IOS'):
        if (k9[a+2]=='XE'):
            ios_ver='cisco_xe'
        else:
            ios_ver='cisco_ios'
    else:
        ios_ver='cisco_nxos'
        
    print(ios_ver)


    verdict['soft_ver']=ios_ver
    if ios_ver=='cisco_nxos':
        if 'BIOS:' in k9 and 'kickstart:' in k9:
            var=k9.index('BIOS:')
            var3=k9.index('kickstart:')
            verdict['version']="BIOS: "+k9[var+2]+" Kickstart: "+k9[var3+2]
        if 'uptime' in k9 and 'second(s)' in k9:
            var=k9.index('uptime')
            var2=k9.index('second(s)')
            verdict['uptime']=' '.join(k9[var+2:var2+1])
        if 'Hardware' in k9:
            var=k9.index('Hardware')
            verdict['hardware']=' '.join(k9[var+1:var+3])
        if 'Reason:' in k9:
            var=k9.index('Reason:')
            verdict['reload_reason']=k9[var+1]
        
    elif ios_ver=='cisco_xe':
        if 'weeks,' in k9 and 'minutes' in k9:
            var=k9.index('weeks,')
            var2=k9.index('minutes')
            verdict['uptime']=' '.join(k9[var-1:var2+1])
        if 'Last' in k9 and 'This' in k9:
            var=k9.index('Last')
            var2=k9.index('This')
            verdict['reload_reason']=' '.join(k9[var+3:var2])

        if 'Version' in k9:
            var=k9.index('Version')
        
            verdict['version']=k9[var+1]
        
            #var=k9.index('Release')
            #verdict['hardware']=k9[var+4]  
        
            
        
    else:
        if 'Version' in k9:
            var=k9.index('Version')
            verdict['version']=' '.join(k9[var+1][:-1])
        if 'Software,' in k9:
            var=k9.index('Software,')
            verdict['hardware']=k9[var+1]  
        if 'uptime' in k9 and 'minutes' in k9:
            var=k9.index('uptime')

            var2=k9.index('minutes')
            verdict['uptime']=' '.join(k9[var+2:var2+1]) 
        if 'reason:' in k9 and 'This' in k9:           
            var=k9.index('reason:')
            var2=k9.index('This')
            verdict['reload_reason']=' '.join(k9[var+1:var2])

    

    print(verdict)





    
    boo=True
    while boo:
            try:
                
                ssh=ConnectHandler(device_type=ios_ver,host=dst,username="rit",password="CMSnoc$1234")
                boo=False
            except Exception as e:
                boo=True
                print(" Connection error, trying again ",e,dst)
                ping_stat['terminate']='true'
                ping_stat['ssh_failure']='true'
                ping_stat['ssh_err_ip'].append(dst)
                ssh_failure_any=True
                return entry,exit,entryrev,setofnames,ping_stat
                
                #return exit,entryrev,g.intojson,ping_stat
    boo=True
    while boo:
        try:
            name=ssh.find_prompt()
            boo=False
        except Exception as e:
            print(str(e))
            print("Find Prompt errTrying Again")
            boo=True
            
    name=name[:-1]
    honame.add(name)

    if name not in setofnames:
        setofnames.add(name)
        dictofnames[name]=count
        k1=router(name)
        arr.append(k1)
        g.dictofobj[name]=k1
        g.dictofobj[name].addconnect(ssh)
        g.dictofobj[name].addsshpass(True)
        count+=1

    g.dictofobj[name].gennodedict['version']=verdict
    
    if ios_ver=='cisco_nxos':
        
        ret=ssh.send_command('sh ip int brief | include '+dst)
        ret=ret.split()
        print(ret)
        entry_int_dst=ret[0]
        print("entry on dest "+entry_int_dst)
        if name not in entry.keys():
            entry[name]=set()
        p=''
        
        p=entry_int_dst+' '+'directly'
        entry[name].add(p)

        ctobj=dictofnames[name]
        arr[ctobj].addentry(p)
        g.dictofobj[name].adddictip(entry_int_dst,dst)

        p=''
        entryrev['directly']=set()
        p=name+' '+entry_int_dst
        entryrev['directly'].add(p)

    else:
                                                
        boo=True
        while boo:
            try:
                ret=ssh.send_command("sh ip int brief | include "+dst)
                boo=False
            except:
                print("8 Exception Handled- Trying again")
                boo=True
            print(" return from sh ip int brief | inc dest ")
            print(ret)
            if not ret:
                boo=True
            elif isinstance(ret,list):
                print("8 Return from sh ip int brief is a list, trying again")
                boo=True
            elif len(ret.split())<6:
                boo=True
                print("8 Trying Again")
            else:
                boo=False

        ret=ret.split()
        #print(ret)
        if name not in entry.keys():
            entry[name]=set()
        p=''
        p=ret[0]
        p=p+' '+'directly'
        entry[name].add(p)

        hop=ret[0]
        ip=dst

        ctobj=dictofnames[name]
        arr[ctobj].addentry(p)
        g.dictofobj[name].adddictip(hop,ip)

        p=''
        entryrev['directly']=set()
        p=name+' '+ret[0]
        entryrev['directly'].add(p)

    print("Entry interfaces ")
    print(entry)
    print()
    print(" Exit  interfaces ")
    print(exit)

    print()
    print(" Entry Reverse ")
    print(entryrev)

    return entry,exit,entryrev,setofnames,ping_stat