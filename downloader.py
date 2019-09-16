from multiprocessing import Process,Event
from urllib.request import urlretrieve,Request,urlopen
from time import sleep
import os,re,sys,argparse,urllib

options = { #replace with settings file later
    "concurrentDownloads":1,
    "downloadProgress":False,
    "retryDelay":5
}

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
        except urllib.error.HTTPError as e:
            print("HTTP Error:")
            print(e)
            sleep(options["retryDelay"])
            retries += 1
        
    file.close()
    if e != None:
        e.set()


#DL(["http://www.newgrounds.com/audio/download/626468"],["file.mp3"])
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
            sleep(0.1)
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
    matches = []
    matches_genres = []
    page_i = 1
    more = True
    while more:
        url = "https://"+username+".newgrounds.com/"+dlType+"/page/"+str(page_i)
        print("Fetching '{}'...".format(url))
        req = Request(url, headers={"User-agent":"Mozilla/5.0", "x-requested-with": "XMLHttpRequest"})
        page = str(urlopen(req).read(),encoding="UTF-8")
        matches += re.findall('<a href=.*?newgrounds\.com.*?'+dlType+'.*?listen.*?([0-9]+).*?title\=.*?\"(.+?)\\\\\">', page)
        matches_genres += re.findall('detail-genre.*?(?:\s)+([ \w]+).*?div>', page)
        more = re.search("\"more\"\:null", page) is None
        page_i += 1
    print("Found {} songs.".format(str(len(matches))))
    urls = ["https://www.newgrounds.com/audio/download/{}/".format(matches[i][0]) for i in range(len(matches))]
    files = [folder+username+"\\"+matches_genres[i].replace("Song","").strip()+"\\"+matches[i][1]+".mp3" for i in range(len(matches))]
    if not os.path.exists(folder+username):
        os.mkdir(folder+username)
        
    DL(urls,files)


def getArgParser():
    p = argparse.ArgumentParser(description="Newgrounds music downloader")
    p.add_argument("-n", type=int, default=4, dest="threads", help="Sets the number of files to download concurrently. Should speed up downloads on fast connections.")
    p.add_argument("-t", type=float, default=5, dest="delay", help="Delay (in seconds) to wait before retrying a failed download.")
    p.add_argument("username", nargs="+", help="List of usernames whose songs you wish to download.")
    return p


if __name__ == '__main__':
    args = getArgParser().parse_args()
    options["concurrentDownloads"] = args.threads
    options["retryDelay"] = args.delay
    for user in args.username:
        print("\n\nParsing {}...".format(user))
        getFiles(user)
    
    
