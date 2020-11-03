


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
    return random.choice(l)

def addToList(path,item):
    """Adds item to path. Does not check if it's already present."""
    f = open(path,"a")
    f.write(str(item)+"\n")
    f.close()

def removeFromList(path, key):
    with open(path, "r") as f:
        list = f.readlines()#.split("/n")
        list = [x.strip("\n") for x in list]

    with open(path, "w") as f:
        for x in list:
            if str(key) in x:
            elif str(key) not in x:
                f.write(x + "\n")
            else:
                pass
    
    scrubList(path)

def isOnList(path,item,val):
    """Checks to see if this is on the list in the file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    i = 0;
    #print("{} in {}".format(str(item),outlist))
    for thing in outlist:
        i = i + 1;
        if( str(item) == thing):
            #print("{} is {}".format(str(item),thing))
            if(val):
                return i
            return True
    if(val):
        return -1
    return False
