from bottle import request, response
import glob
import pickle
import random
import os

SESSIONDIR = "sessions/"

class session:
    #Objects of this class will allow for easy session management in a bottle-py based, web app
    
    def __init__(self, secret_key="reallyinsecurepassword"):
        #Set the secret key to sign the cookies
        self.sessionid = None
        self.secret_key = secret_key
        self.sess = {}
        #Look for a session cookie
        #If one exists, then open the corresponding session file. Otherwise, continue with a blank session.
        try:
            self.sessionid = request.get_cookie("sessionid", secret=self.secret_key)
            #Load the session variables from file
            f = open(SESSIONDIR+str(self.sessionid)+".ses", "rb")
            self.sess = pickle.load(f)
            f.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            #If the file doesn't exist, continue with a blank session.
            pass
    
    def set(self, arg1, arg2):
        self.sess[arg1] = arg2
    
    def read(self, arg1):
        return self.sess[arg1]
    
    def close(self):
        #save the session variables back to file
        if not os.path.exists(SESSIONDIR):
            os.makedirs(SESSIONDIR)
        if self.sessionid == None:
            #generate a new sessionid
            ids = [x[len(SESSIONDIR):-4] for x in glob.glob(SESSIONDIR+"*.ses")]
            while True:
                self.sessionid = '%08x' % random.randrange(1 << 32)
                if self.sessionid not in ids:
                    break
        path = SESSIONDIR+str(self.sessionid)+".ses"
        f = open(path,"wb")
        pickle.dump(self.sess, f)
        f.close()
        #set the sessionid in the user cookie
        response.set_cookie("sessionid", self.sessionid, secret=self.secret_key)
        