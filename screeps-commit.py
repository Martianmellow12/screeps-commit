# Screeps Commit
#
# Written by Michael Kersting Jr.
import base64
import requests
import os
import json
import argparse
import sys

#
#
# Basic Encode - Used to send credentials
def basicEncode(usr, pwd):
    data = "%s:%s" % (usr, pwd)
    data = data.encode("ASCII")

    # We need a raw string, so we'll strip it out
    data = str(base64.b64encode(data))
    return data[2:len(data)-1]

#
#
# Generate Commit - Generates a commit from the base DIR's files
def generateCommit(baseDir, branch):
    # First create the base dictionary
    commit = dict()
    commit["branch"] = branch
    commit["modules"] = dict()

    # Next add modules from the base DIR
    for i in os.listdir(baseDir):
        # Continue if the file isn't a JSON file
        if i[len(i)-3:] != ".js": continue

        # Add the file and its contents to the module list
        moduleName = i[:len(i)-3]
        moduleFileStream = open(os.path.join(baseDir, i), "r", encoding="utf8")
        commit["modules"][moduleName] = moduleFileStream.read()
        moduleFileStream.close()

    # Return the commit
    return commit

#
#
# Push Commit - Push a generated commit to a Screeps branch
def pushCommit(usr, pwd, commit):
    # Create headers for the POST request
    headers = {"Content-Type": "application/json; charset=utf-8"}

    # Create a request
    req = requests.post("https://screeps.com/api/user/code", headers=headers, auth=(usr, pwd), data=json.dumps(commit))
    return (req.status_code, req.text)

#
#
# Main Program
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--branch", help="The branch to commit to (defaults to \"default\")")
parser.add_argument("directory", help="The top directory of your code")
args = parser.parse_args()

# Set the default branch, if necessary
branch = args.branch
if branch == None: branch = "default"

# Check to see if there's a config file, and create one if there's not
if not os.path.isfile("screeps-commit.config"):
    print("Config file doesn't exist, creating now")
    print("Please enter your Screeps login information (it will only be stored locally)")
    usr = input("Username: ")
    pwd = input("Password: ")
    print("Saving to config file...", end="")
    with open("screeps-commit.config", "w") as fileout:
        fileout.write(json.dumps({"username":usr, "password":pwd}))
    print("Done")

# Generate the commit and confirm that the user wants to push their code
print("Generating commit...", end="")
commit = generateCommit(args.directory, branch)
print("Done\n")
print("The following modules will be pushed to the branch \"%s\":" % commit["branch"])
for i in commit["modules"].keys():
    print("\t%s" % i)
print("\nContinue? [y/n]", end="")
if input().lower() == "n": sys.exit(0)

# Push the commit
print("Pushing the commit...", end="")
with open("screeps-commit.config", "r") as filein:
    login = json.loads(filein.read())
pushCommit(login["username"], login["password"], commit)
print("Done")
