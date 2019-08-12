import requests
import json
import piexif
import os
import time

newSession = requests.Session() # init new session
total = 0 # total images saved in current session
tagDelimiter = "%20" # delimiter between tags
pageCounter = 0
sapi_key = "" # insert here your api key (take it from gelbooru account settings)
suser_id = "" # insert here your user id (take it from gelbooru account settings)
default_path = "C:/pics/"
random_path = "C:/pics/random/"

additional_tag = "" # used in all options
main_tag = "" # used in 2nd option
improvement_tag = "" # leave empty or "sort:score:desc"

def insert_tags(name,tags):
    """ insert tags into image description """
    try:
        undtags = tags.split(" ")
        tages = ""
        for i in undtags:
            tages += i + ";"
        zeroth_ifd = {40094: tages.encode('utf16')}
        exif_bytes = piexif.dump({"0th":zeroth_ifd})
        piexif.insert(exif_bytes,name)
        return 1
    except piexif._exceptions.InvalidImageDataError:
        print ("[ERR] Can't add tags to this image!")
        return 0

def check_artist(tags,par):
    if par == "":
        ready_url = f"https://gelbooru.com//index.php?page=dapi&s=tag&q=index&json=1&limit=1000&names={tags}&api_key={sapi_key}&user_id={suser_id}"
        print ("[!] Request to server")
        askForTags = newSession.get(ready_url.replace(" ", tagDelimiter)) # send get request for tags
        tagsToJson = json.loads(askForTags.text)
        artistName = "" # ident artist name variable
        for tag in tagsToJson:
            if tag["type"] == "artist":
                artistName = tag["tag"].replace(':','').replace('<','').replace('>','').replace('"','').replace('/','').replace('\\','').replace('|','').replace('?','').replace('*','') # clean artist name so it can be used while creating folders
                if (artistName != "" and artistName != " "): # be sure that all is going ok
                    return artistName
                else:
                    print ("[ERR] Artist name is empty.")
                    return 0
        if artistName == "":
            print ("[ERR] Can't find artist")
            return 0
    else:
        return par

def bot_ident(pageId):
    """ ident bot variables and etc ... """
    api_key = f"&api_key={sapi_key}&user_id={suser_id}" # auth data
    api_access = f"https://gelbooru.com//index.php?page=dapi&s=post&q=index&limit=1000&pid={pageId}&json=1&" # increase limit to 100
    tags = [additional_tag, main_tag, improvement_tag] # combine usefull tags

    # load tags from user input to search request
    if len(tags) != 0: # if tags not null
        api_access += "tags=" # add tags name
        for items in tags:
            api_access += items + tagDelimiter # add tags to search string
        api_access += api_key # add authentication
        return api_access # return final string that will go to get request
    else:
        print ("[ERR] Tags not setted!")
        return 0

def bot_main(api_line,par,artist):
    global total
    if api_line != 0 :
        print ("[!] Request to server")
        baka = newSession.get(api_line) # send get request to gelbooru
        tojson = json.loads(baka.text) # load response to json, it returns 100 images
        lilCounter = 0
        if len(tojson) == 0:
            return 0 # we reach the end

        for imageString in tojson: # take one by one
            print ("Images was saved: +",total,"| Progress:",lilCounter,"/","1000","| Pages:",pageCounter)
            lilCounter += 1
            getUrl = imageString["file_url"] # main url to download
            getName = imageString["image"] # name with hash to use in image name
            getTags = imageString["tags"] # tags to add to image description

            randomFolder = random_path + str(getName) # ident random folder

            print ("[OK] Image name:", getName) # print out imageName

            if par == 3:
                checkArtist = check_artist(getTags,artist) # check if artist exists in available tags

            if checkArtist != 0:

                fullImagePath = default_path + checkArtist + "/" + getName # looks like C:/pics/artist/123.jpg
                if not os.path.exists(os.path.dirname(fullImagePath)): 
                    os.makedirs(os.path.dirname(fullImagePath)) # make new dir if not yet created
                
                toBeSure = 0 # marker
                for image in os.listdir(default_path + checkArtist):
                    if image == getName:
                        print ("[ERR] Image already was saved!")
                        toBeSure = 1
                        break

                # continue here
                if toBeSure == 0:
                    with open(fullImagePath, 'wb+') as f: # open to save image
                        f.write(requests.get(getUrl).content) # save image
                        print ("[OK] Image saved to", checkArtist + "!")
                        insert_tags(fullImagePath, getTags.replace(" ", ";"))
                        total += 1 # increase total saved images counter

            else: # if artist name not found

                toBeSure = 0 # marker
                for image in os.listdir(random_path):
                    if image == getName:
                        print ("[ERR] Image already was saved!")
                        toBeSure = 1
                        break
                
                if toBeSure == 0:
                    with open(randomFolder, 'wb+') as f:
                        f.write(requests.get(getUrl).content) # save image
                        print ("[OK] Image saved to random!")
                        insert_tags(randomFolder, getTags.replace(" ", ";"))
                        total += 1 # increase total saved images counter
        lilCounter = 0
    else:
        print ("[ERR] Please specify tags!")
        return 0

def main():
    global total
    global pageCounter
    global additional_tag

    while True:
        
        askUser = input("""
    GelBooru Parser v0.5:
                    
    1. Collect all images by main tag.
    2. Parse specified artist. 
    3. Fill existed artists in folder.

    Your choice: """)

        if (askUser == "1"):
            with open('2_progress.txt') as f: # load progress from file
                pid, iid = f.read().split((":"))
                pageCounter = int(pid)
                # todo: add image ids
            currentDirs = len(os.listdir(default_path)) # check count current artists
            while pageCounter >= 0:
                print ("/------------------------------\\")
                print ("PageId:",pageCounter,"| Authors:", len(os.listdir(default_path)),"/ +",len(os.listdir(default_path))-currentDirs, "| Images: +", total)
                lets_ident = bot_ident(pageCounter)
                try:
                    run_it = bot_main(lets_ident,1,"")
                except json.decoder.JSONDecodeError:
                    print ("Probably reach limit. Exit.")
                    return 1
                print ("\\------------------------------/")
                if run_it != 0:
                    pageCounter += 1
                    with open("2_progress.txt", "w") as f:
                        f.write(str(pageCounter) + ":" + str(0)) # todo: add image ids
                else: # reach limit of images
                    print ("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>> Task finished!\n\n")
                    return 0
        elif (askUser == "2"):
            cleanProgress = input ("[INF] Do you want to clean up progess to 0:0? y/n: ")
            if (cleanProgress == "y"):
                with open("artist.txt", "w") as f:
                    f.write("0:0")
                    print ("[OK] Progess cleaned!")
            with open('artist.txt') as f: # load progress from file
                pid, iid = f.read().split((":"))
                pageCounter = int(pid)
                # todo: add image ids
            additional_tag = input ("[INF] Please specify artist name: ")
            while pageCounter >= 0:
                currentDirs = len(os.listdir(default_path))
                print ("/------------------------------\\")
                print ("PageId:",pageCounter,"| Authors:", len(os.listdir(default_path)),"/ +",len(os.listdir(default_path))-currentDirs, "| Images: +", total)
                lets_ident = bot_ident(pageCounter)
                try:
                    run_it = bot_main(lets_ident,2,"")
                except json.decoder.JSONDecodeError:
                    print ("Probably reach limit. Exit.")
                    return 1
                print ("\\------------------------------/")
                if run_it != 0:
                    pageCounter += 1
                    with open("artist.txt", "w") as f:
                        f.write(str(pageCounter) + ":" + str(0)) # todo: add image ids
                else: # reach limit of images
                    print ("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>> Task finished!\n\n")
                    return 0

        elif (askUser == "3"):
            cleanProgress = input ("[INF] Do you want to clean up progess to 0:0? y/n: ")
            if (cleanProgress == "y"):
                with open("artist.txt", "w") as f:
                    f.write("0:0")
                    print ("[OK] Progess cleaned!")
            currentDirs = len(os.listdir(default_path))
            with open('artist.txt') as f: # load progress from file
                pid, iid = f.read().split((":"))
                pageCounter = int(pid)
                # todo: add image ids
            artists = os.listdir(default_path) # names of current artist
            for i in artists:
                print ("Collecting artist:",i)
                additional_tag = i.replace("\n","")
                with open("updatedartists.txt") as f:
                    content = f.readlines()
                if (additional_tag + "\n" not in content):
                    while pageCounter >= 0:
                        print ("/------------------------------\\")
                        print ("PageId:",pageCounter,"| Completed Authors:", len(content),"/",len(os.listdir(default_path)), "| Images: +", total)
                        lets_ident = bot_ident(pageCounter)
                        try:
                            run_it = bot_main(lets_ident,3,i)
                        except json.decoder.JSONDecodeError:
                            print ("Empty author. Next.")
                            pageCounter = 0
                            with open("updatedartists.txt", "a") as f:
                                f.write(i + "\n")
                            break
                            time.sleep(1)
                        print ("\\------------------------------/")
                        if run_it != 0:
                            pageCounter += 1
                        else: # reach limit of images
                            pageCounter = 0
                            with open("updatedartists.txt", "a") as f:
                                f.write(i + "\n")
                            break # next author
                            time.sleep(1)
                else:
                    pageCounter = 0
                    print ("[ERR] Artist", additional_tag ,"already parsed before!")
        else:
            print ("Please select between existed items.")
    print ("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>> Task finished!\n\n")

main()