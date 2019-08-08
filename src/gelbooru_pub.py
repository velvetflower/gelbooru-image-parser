import requests
import sys
import json
from time import sleep
import os
import piexif

succ = 0

def insert_tags(name,tags):
    try:
        undtags = tags.split(" ")
        tages = ""
        for i in undtags:
            tages += i + ";"
        zeroth_ifd = {40094: tages.encode('utf16')}
        exif_bytes = piexif.dump({"0th":zeroth_ifd})
        piexif.insert(exif_bytes,name)
        print ("[OK] Tags added!")
    except piexif._exceptions.InvalidImageDataError:
        print ("[ERR] Can't add tags to this image!")

class GelBot:
    global pageId
    global cpectag
    global succ
    def __init__(self, **kwargs):
        self.api_key = "&api_key=INSERT&user_id=INSERT"
        self.api_access = f"https://gelbooru.com//index.php?page=dapi&s=post&q=index&limit=5&pid={pageId}&json=1&"
        self.tagDelimiter = "%20"
        self.tags = [cpectag,"sort:score:desc"]
        self.newsess = requests.Session() # init new session

        # load tags from user input to search request
        if len(self.tags) != 0:
            self.api_access += "tags=sort:score:desc%20"
            for items in self.tags:
                self.api_access += items + self.tagDelimiter # add tags to search
            self.api_access += self.api_key
            #print ("[OK] Tags loaded!")
        else:
            print ("[ERR] Tags not setted!")
            sys.exit(status=0, message=None)
        
    def analyze_json(self, cntr):
        global succ
        #print ("Used url:",self.api_access)
        self.baka = self.newsess.get(self.api_access)
        self.tojson = json.loads(self.baka.text)
        #print(f"Len: {len(self.tojson)}")
        getUrl = self.tojson[cntr]["file_url"]
        getHash = self.tojson[cntr]["hash"]
        getName = self.tojson[cntr]["image"]
        getWidth = self.tojson[cntr]["width"]
        getHeight = self.tojson[cntr]["height"]
        getTags = self.tojson[cntr]["tags"]

        currentimagename = "random" + str(getName)
        justname = str(getName)

        if (getWidth > 50 or getHeight > 50):
            print ("[OK] Current image name:", justname)
            
            listimagesq = os.listdir("images")
            kaka = 0
            for i in listimagesq:
                if (justname in os.listdir("images" + i)):
                    kaka = 1
                    break

            if (kaka == 0):
                tagUrl = f"https://gelbooru.com//index.php?page=dapi&s=tag&q=index&json=1&limit=300&names={getTags}&api_key=INSERT&user_id=INSERT"
                kk = self.newsess.get(tagUrl.replace(" ",self.tagDelimiter))
                sleep(1)
                tagToJson = json.loads(kk.text)

                artistName = ""
                bakartist = 0
                for i in tagToJson:
                    if (i["type"] == "artist"):
                        #print ("[OK] Found artist:",i["tag"])
                        artistName = i["tag"].replace(':','').replace('<','').replace('>','').replace('"','').replace('/','').replace('\\','').replace('|','').replace('?','').replace('*','')
                        if (artistName != "" and artistName != " "):
                            #print (f"[OK] Artist name is '{artistName}'")
                            bakartist = 1
                if (bakartist == 0):
                    print ("[ERR] Can't find artist :(")

                if (bakartist == 1):
                    fullPath = "images" + artistName + "/" + justname
                    if not os.path.exists(os.path.dirname(fullPath)):
                        os.makedirs(os.path.dirname(fullPath))
                    with open(fullPath, 'wb+') as f:
                        f.write(requests.get(getUrl).content) # save image
                        print ("[OK] Image saved to", artistName + "!")
                        insert_tags(fullPath,getTags)
                        succ += 1
                    print ("[INF] Total saved:",succ) 
                    print ("=========================================")
                else:
                    with open(currentimagename, 'wb+') as f:
                        f.write(requests.get(getUrl).content) # save image
                        print ("[OK] Image saved to random!")
                        insert_tags(currentimagename,getTags.replace(" ", ";"))
                        succ += 1
                    print ("[INF] Total saved:",succ) 
                    print ("=========================================")
            else:
                print ("[ERR] Image already was saved!")
                print ("[INF] Total saved:",succ) 
                print ("=========================================")
        else:
            print ("[ERR] Image has low size!")
            print ("[INF] Total saved:",succ) 
            print ("=========================================")


askuser = input("""
GelBooru Parser v0.2:
                
1. Parse specified artist.
2. Collect all images by tag.
3. Fill existed artists in folder.

Your choice: """)
if (askuser == "2"):
    with open('progress.txt') as f:
        variable=f.read()
        baka, beka = variable.split((":"))
        pageId = int(baka)
        imageId = int(beka)
    cpectag = "1girl"
    beka = 1
    badboys = 0
    while beka == 1:
        print ("[INF] Exceptions:",badboys)
        try:
            print ("=========================================")
            print ("[OK] Current pageId:",pageId,"& imageId:",imageId)
            sheet = GelBot()
            sheet.analyze_json(imageId)
            if (imageId == 4):
                pageId += 1
                imageId = 0
            else:
                imageId += 1
            with open("progress.txt", "w") as f:
                f.write(str(pageId) + ":" + str(imageId))
            sleep(1) 
        except Exception as e:
            badboys += 1
            print (e)
            sleep(10)
            if (imageId == 4):
                pageId += 1
                imageId = 0
            else:
                imageId += 1
elif (askuser == "1"):
    askuser2 = input ("[INF] Do you want to clean up progess to 0:0? y/n: ")
    if (askuser2 == "y"):
        with open("artist.txt", "w") as f:
            f.write("0:0")
            print ("[OK] Progess cleaned!")
    with open('artist.txt') as f:
        variable=f.read()
        baka, beka = variable.split((":"))
        pageId = int(baka)
        imageId = int(beka)
    askuser3 = input ("[INF] Please specify artist name: ")
    cpectag = askuser3
    beka = 1
    badboys = 0
    while beka == 1:
        print ("[INF] Exceptions:",badboys)
        try:
            print ("=========================================")
            print ("[OK] Current pageId:",pageId,"& imageId:",imageId)
            sheet = GelBot()
            sheet.analyze_json(imageId)
            if (imageId == 4):
                pageId += 1
                imageId = 0
            else:
                imageId += 1
            with open("artist.txt", "w") as f:
                f.write(str(pageId) + ":" + str(imageId))
            sleep(1) 
        except Exception as e:
            badboys += 1
            print (e)
            break
            if (imageId == 4):
                pageId += 1
                imageId = 0
            else:
                imageId += 1
elif (askuser == "3"):
    askuser2 = input ("[INF] Do you want to clean up progess to 0:0? y/n: ")
    if (askuser2 == "y"):
        with open("artist.txt", "w") as f:
            f.write("0:0")
            print ("[OK] Progess cleaned!")
    with open('artist.txt') as f:
        variable=f.read()
        baka, beka = variable.split((":"))
        pageId = int(baka)
        imageId = int(beka)
    artists = os.listdir("images")
    for i in artists:
        cpectag = i.replace("\n","")
        badboys = 0
        beka = 1
        with open("updatedartists.txt") as f:
            content = f.readlines()
        print ("List of used artists:",content)
        if (cpectag + "\n" not in content):
            sleep(1)
            while beka == 1:
                try:
                    print ("[INF] Exceptions:",badboys,"|","used artists:",len(content),"/",len(artists))
                    print ("=========================================")
                    print ("[OK] Current pageId:",pageId,"& imageId:",imageId)
                    print ("[INF] Current artist:",i)

                    sheet = GelBot()
                    sheet.analyze_json(imageId)
                    if (imageId == 4):
                        pageId += 1
                        imageId = 0
                    else:
                        imageId += 1
                    with open("artist.txt", "w") as f:
                        f.write(str(pageId) + ":" + str(imageId))
                    sleep(1)
                except Exception as e:
                    print ("gak")
                    badboys += 1
                    print (e)
                    with open("updatedartists.txt", "a") as f:
                        f.write(i + "\n")
                    pageId = 0
                    imageId = 0
                    break
        else:
            print ("[ERR] Artist", cpectag ,"already parsed before!")
