import os
from os.path import isfile, join
from os import path

"""General purpose library for treating a text file like a dictionary."""

#To use:
#from keyvaluemanagement import *
#at beginning of file.

#Primary Functions- You'll be using these:
#kvSetValue(path,key,value) - Sets a key to a value. Overwrites if already present.
#kvAddValue(path,key,value) - Sets a key to a value. DOES NOTHING if already present.
#kvRemoveKey(path,key) - Deletes key and value.
#kvGetValue(path,key) - Get Value from key. Returns None if not present.
#kvGetKey(path,value) - Get key from a value. Pointless and unreliable - but might be useful if you're sure there aren't duplicates, as it only returns one key.


seperator = "====="

def addToList(path,item):
    """Adds item to path. Does not check if it's already present."""
    f = open(path,"a")
    f.write(str(item)+"\n")
    f.close()

def scrubList(path):
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    
    f = open(path,"w") #Clear old file
    f.close()
    
    for item in outlist:
        if(item != ""):
            addToList(path,item)

def kvMakeList(path):
    """Return a list of RAW entries from this file. No seperation."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    return outlist

def kvGetKeys(path):
    """Gets all keys from a file."""
    work = kvMakeList(path)
    
    outlist = []
    for ent in work:
        kv = ent.split(seperator)
        outlist.append(kv[0])
    
    return outlist


def kvGetValues(path):
    """Gets all values from a file."""
    work = kvMakeList(path)
    
    outlist = []
    for ent in work:
        kv = ent.split(seperator)
        outlist.append(kv[-1])
    
    return outlist


def kvGetKeysValues(path):
    """Gets all key value pairs from a file."""
    work = kvMakeList(path)
    
    keys = []
    values = []
    for ent in work:
        kv = ent.split(seperator)
        keys.append(kv[0])
        values.append(kv[-1])
    
    
    return keys, values


def kvAddValue(path,key,value):
    """Adds item to path. If already present, silently fails."""
    if(kvGetValue(path,key) == None):
        f = open(path,"a")
        f.write(str(key)+seperator+str(value)+"\n")
        f.close()
    else:
        print("[kvAddValue] Key already present: {}".format(key))


def kvSetValue(path,key,value):
    """Adds item to path. If already present, overwrites the previous value."""
    if(kvGetValue(path,key) == None):
        f = open(path,"a")
        f.write(str(key)+seperator+str(value)+"\n")
        f.close()
    else:
        kvRemoveKey(path,key)
        kvSetValue(path,key,value)

def kvRemoveKey(path, key):
    """Given a key, remove it from the file."""
    with open(path, "r") as f:
        listx = f.readlines()#.split("/n")
        listx = [x.strip("\n") for x in listx]

    with open(path, "w") as f:
        for x in listx:
            if x.startswith(str(key)) == False:
                f.write(x + "\n")
            elif x == listx[(len(listx)-1)] and listx[(len(listx)-1)] != "\n":
                f.write("\n")
            else:
                pass
    
    scrubList(path)

def kvGetValue(path,key):
    """Gets value from key. Returns None if not present."""
    keys, values = kvGetKeysValues(path)
    #print("{} in {}".format(str(item),outlist))
    
    for i in range(len(keys)):
        if str(keys[i]) == str(key):
            return values[i]
    return None


def kvGetKey(path, value):
    """Gets key from value. Returns None if not present."""
    keys, values = kvGetKeysValues(path)
    #print("{} in {}".format(str(item),outlist))
    try: #If it can find the id in keys, it says so
        x = keys.index(str(value))
    except ValueError:
        return None
    else:
        return keys[x]
    
def kvGetKey2(path,value): #Specially made (Pardon my awful code) for the react2join module to avoid breaking compat. w/ kvGetKey
    """Gets key from value. Returns None if not present."""
    keys, values = kvGetKeysValues(path)
    #print("{} in {}".format(str(item),outlist))
    
    for i in range(len(keys)):
        if str(values[i]) == str(value):
            return keys[i]
    return None
