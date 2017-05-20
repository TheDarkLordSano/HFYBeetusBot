import praw
import OAuth2Util
#import ipdb
#print "Imports complete"

red = praw.Reddit("OAuthentication for /u/HFYsubs")
OAuthen = OAuth2Util.OAuth2Util(red, configfile="Authent.ini")

OAuthen.refresh()

