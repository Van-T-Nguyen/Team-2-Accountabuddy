


"""Simple commands for reading from and modifying text files."""






def scrubList(path):
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    
    f = open(path,"w") #Clear old file
    f.close()
    
    for item in outlist:
        if(item != ""):
            addToList(path,item)


def makeList(path):
    """Return a list of ints from this file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    return outlist

def getEntry(path):
    """Gets a random entry from this text file"""
    l = makeList(path)

def addToList(path,item):
    """Adds item to path. Does not check if it's already present."""
    f = open(path,"a")
    f.write(str(item)+"\n")
    f.close()

def removeFromList(path, item):
    with open(path, "r") as f:
        list = f.readlines()#.split("/n")
        list = [x.strip("\n") for x in list]

    with open(path, "w") as f:
        for x in list:
            if x != str(item):
                f.write(x + "\n")
            elif x == list[(len(list)-1)] and list[(len(list)-1)] != "\n":
                f.write("\n")
            else:
                pass
    
    scrubList(path)

def isOnList(path,item):
    """Checks to see if this is on the list in the file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    #print("{} in {}".format(str(item),outlist))
    for thing in outlist:
        if( str(item) == thing):
            #print("{} is {}".format(str(item),thing))
            return True
    
    return False
