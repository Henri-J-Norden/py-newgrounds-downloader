options = { #replace with settings file later
    "concurrentDownloads":1,
    "downloadProgress":False
    }


from multiprocessing import Process,Event
from urllib.request import urlretrieve,Request,urlopen
from time import sleep
import os,re,sys

downloadCount = 0
downloaders = []
downloaderArgs = []
downloadersDone = []
"""

DLProgressTracker = []
def DLProgress(blocks,blockSize,totalSize,percent=101): #display download progress every 25%
    global DLProgressTracker
    status = int((blocks*blockSize/totalSize)*100)
    if status == 0 and status not in DLProgressTracker:
        DLProgressTracker.append(clock())
    if status%percent == 0:
        if status not in DLProgressTracker:
            DLProgressTracker.append(status)
            #stdout.write(basename(argv[2])+" progress: "+str(status)+"%% (%0.2fMB) of %0.2fMB"%(blocks*blockSize/1024/1024,totalSize/1024/1024)+"\n")
            #stdout.flush()
    if status == 100:
        stdout.write(basename(argv[2])+" finished with avg download speed of %0.2fMB/s"%((totalSize/1024/1024)/(clock()-DLProgressTracker[0]))+"\n")
        stdout.flush()
        #DLProgressTracker = [] #not necessary, since the function is only used once
"""
def downloader(url,target,e=None):
    req = Request(url,headers={"User-agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"})
    if not os.path.exists(os.path.dirname(target)):
        os.mkdir(os.path.dirname(target))
    file = open(target,"wb")
    success = False
    retries = 0
    while not success and retries < 7:
        try:
            file.write(urlopen(req).read())
            success = True
        except urllib.error.HTTPError:
            sleep(11)
            retries += 1
        
    file.close()
    if e != None:
        e.set()


def DL(urlList, targetList):
    global downloadCount
    args = [(urlList[x], targetList[x]) for x in range(len(urlList))]
    while args != []:
        shift = 0
        for i in range(downloadCount):
            if downloaderArgs[i+shift][2].is_set():
                del(downloaders[i+shift])
                print("Finished downloading "+os.path.basename(downloaderArgs[i+shift][1]))
                del(downloaderArgs[i+shift])
                downloadCount -= 1
                shift -= 1
        if downloadCount >= options["concurrentDownloads"]:
            sleep(0.05)
        else:
            while downloadCount < options["concurrentDownloads"] and args != []:
                arg = [x for x in args.pop()]
                arg.append(Event())
                arg = tuple(arg)
                downloaders.append(Process(target=downloader,args=arg))
                downloaders[-1].start()
                downloaderArgs.append(arg)
                print("Started downloading "+os.path.basename(arg[1]))
                downloadCount += 1
    

def getFiles(username,folder=".\\",dlType="audio"):
    req = Request("http://"+username+".newgrounds.com/"+dlType+"/",headers={"User-agent":"Mozilla/5.0"})
    page = str(urlopen(req).read(),encoding="UTF-8")
    matches = re.findall('<a href="(http://www.newgrounds.com/'+dlType+'/listen[a-zA-Z0-9\-_/]*)">(.*)</a>[ </td>\n]*([a-zA-Z0-9 _-]*)</td>',page)
    urls = [matches[i][0].replace("listen","download") for i in range(len(matches))]
    files = [folder+username+"\\"+matches[i][2].replace(" Song","")+"\\"+matches[i][1]+".mp3" for i in range(len(matches))]
    if not os.path.exists(folder+username):
        os.mkdir(folder+username)
    #print(len(files),len(urls))
    #print("\n".join(files))
    #input(urls)
        
    DL(urls,files)
    #for i in range(len(urls)):
    #    print(urls[i])
    #    downloader(urls[i],files[i])

if __name__ == '__main__':    
    #DL(["http://www.newgrounds.com/audio/download/626468"],["file.mp3"])
    getFiles("indigorain")
    
    
