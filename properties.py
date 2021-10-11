#!/usr/bin/python3
import os, json

#os_env = json.load("properties/os_env.json")
#itdk_version = json.load("properties/itdk_version.json")
#db = json.load("properties/db.json")


# itdk_folder_loc = home + "/Downloads/ITDK-" + itdk_year + "-" + itdk_month + "/"
# itdk_folder_loc = "/media/" + user + "/Backup Plus/ITDK-" + itdk_year + "-" + itdk_month + "/"

itdk_file_types = [".nodes", ".links", ".nodes.as", ".nodes.geo", ".ifaces"]



def deserialize_os_env(file="properties/os_env.json"):
    f = open(file)
    deserialized = json.load(f)
    f.close()
    return deserialized

def deserialize_itdk_version(file="properties/itdk_version.json"):
    f = open(file)
    deserialized = json.load(f)
    f.close()
    return deserialized

def deserialize_db(file="properties/db.json"):
    f = open(file)
    deserialized = json.load(f)
    f.close()
    return deserialized



# Get OS properties
def os_env__os(os_env):
    return (os_env["os"])

def os_env__username(os_env):
    return (os_env["username"])

def os_env__home(os_env):
    return os.path.expanduser("~" + os_env__username(os_env))



# Get ITDK version properties
def itdk_version__ip_version(itdk_version):
    return (itdk_version["ip_version"])

def itdk_version__year(itdk_version):
    return (itdk_version["year"])

def itdk_version__month(itdk_version):
    return (itdk_version["month"])

def itdk_version__day(itdk_version):
    return (itdk_version["day"])

def itdk_version__url(itdk_version):
    return (itdk_version["url"])

def itdk_version__topo_choice(itdk_version):
    return (itdk_version["topo_choice"])

def itdk_version__compression_extension(itdk_version):
    return (itdk_version["compression_extension"])

def itdk_version__file_location(itdk_version):
    return (itdk_version["file_location"])

def itdk_version__download(itdk_version):
    return (itdk_version["download"])

def itdk_version__decompress(itdk_version):
    return (itdk_version["decompress"])



# Get database properties
def db__driver(db):
    return (db["driver"])

def db__server(db):
    return (db["server"])

def db__name(db):
    return (db["name"])

def db__user(db):
    return (db["user"])

def db__pwd(db):
    return (db["pwd"])
