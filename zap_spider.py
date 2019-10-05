#!/root/anaconda3/envs/pentest/bin/python

# use a python env and make sure these modules are installed "pip instal <module>"
import time
from zapv2 import ZAPv2
import subprocess
import psutil
import os
import sh
import sys
from pprint import pprint

try:
    target = sys.argv[1]
except Exception as e:
    print ("usage: zap_spider.py http://yoursite.com")
    sys.exit()
    

try:
    print('RUNNING ZAP DAEMON on port 8081')
    #define the command and open the ZAP daemon with subprocess module 
    command = './zap.sh -daemon -config api.key=123456 -port 8081 -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true'
    server = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd='/usr/share/zaproxy')
    sh.tail('/root/.ZAP/zap.log')
    time.sleep(10)
    api='123456'
    print (command, api)
    zap = ZAPv2(apikey=api, proxies={'http': 'http://127.0.0.1:8081', 'https': 'http://127.0.0.1:8081'})


    scanid = zap.spider.scan(target)
    time.sleep(2)
    status = zap.spider.scans
    print(status)
    hosts = zap.core.hosts
    print('Spidering Target', hosts)
    #View discovered pages of the spider by scan id
    urls = zap.spider.results(0)
    for url in urls:
        print(url)
except Exception as e:
    pass

#write the list into the new file to capture all unique deduplicated items
list_item3 = sorted(urls)# sort a-z
output_file = './zap_urls.txt' #enter name of your new list which will be placed in the path we gave above
for item in list_item3:
    with open(output_file, 'a+') as file:
        try:
            file.seek(0)
            file.write(str(item)+"\n")#add a line to make it a list otherwise they output side by side
        except Exception as e:
            print(e)
            pass 
with open(output_file,'r+') as file:
    for line in file:
        if line =="\n":
            file.write("REMOVED A LINE")#removing line chars
            
print('zap_urls.txt FILE WAS WRITTEN TO THE CWD')


print('KILLING ZAP DAEMON AND CLEANING UP')

procs_to_kill = ['/usr/share/zaproxy/zap-2.7.0.jar'] #process that stays open after script finishes 

#KILL RUNNING PROCESSES
for proc in psutil.process_iter():
    try:
        pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
        #oddly enough you can't iterate over an integer and so in this case we need to explicitly make the pid key a string 
#         if '1919' in str(pinfo['pid']): #find the process by pid number
        if 'java' in str(pinfo['name']):#looking for zap proxy daemon but will display my script that started it instead by name
            name = proc.name()
            ppid = proc.ppid() #parent process id
            cmd = proc.cmdline() #command line param passed that we need to take action on since we might have another java app open we can't rely on the name solely
            uid = proc.uids()
            pid = pinfo['pid'] #process id
            conn = proc.connections()
            pid_proc = psutil.Process(pid)
            ppid_proc = psutil.Process(ppid)#parent process name 
            print(f"name={name},pid={pid},ppid={ppid},parent_name={ppid_proc},uid={uid},command={cmd[3]}")
            print(f"{proc}\n")
            #TERMINATE THE ZAP PROCESS
        if cmd[3] in procs_to_kill: #match the psutil object needed for killing the process to our matched list above we need the 4th location which speciifes zap
            print("killing:",proc)
            print(pid_proc)
            pid_proc.terminate()#kill processes by pid
            ppid_proc.terminate()#kill parent process in the case child doesn't end
            proc.kill()#trying to kill process by current process matching my if statement
    except Exception as e:
        pass

#kill left over zap java connections on port 8081
for conn in psutil.net_connections():
    if '8081' in str(conn[3][1]): #slicing for the local port of the connection we check if port 8081 exists
        print(conn)
        pid = conn[6] #this is the pid of the connection needed
        proc = psutil.Process(pid) #get the process by the process id
        print(proc)
        proc.terminate() #end the process that was found
