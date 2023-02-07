from bottle import request, response
import glob
import pickle
import random
import os

sessionSettings = {"sessiondir": "sessions/",
                   "extension": ".ses",
                   "store": True}

#Dictionary of volatile sessions
sessions = {}

class session:
    #Objects of this class will allow for easy session management in a bottle.py based web app
    
    def __init__(self, secret_key="reallyinsecurepassword"):
        #Set the secret key to sign the cookies
        self.sessionid = None
        self.secret_key = secret_key
        self.sess = {}
        #Look for a session cookie
        #If one exists, then load the corresponding session data. Otherwise, continue with a blank session.
        try:
            self.sessionid = request.get_cookie("sessionid", secret=self.secret_key)
            sid = str(self.sessionid)
            #Load the session variables from file
            if sessionSettings["store"]:
                f = open(sessionSettings["sessiondir"]+sid+sessionSettings["extension"], "rb")
                self.sess = pickle.load(f)
                f.close()
            else:
                self.sess = sessions[sid]
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            #If the session doesn't exist, continue with a blank session.
            pass
    
    def set(self, name, value):
        self.sess[name] = value
    
    def read(self, name):
        return self.sess[name]
    
    def close(self):
        if self.sessionid == None:
            #generate a new sessionid
            if sessionSettings["store"]:
                ids = [x[len(sessionSettings["sessiondir"]):-len(sessionSettings["extension"])] for x in glob.glob(sessionSettings["sessiondir"]+"*"+sessionSettings["extension"])]
            else:
                ids = sessions.keys()
            while True:
                self.sessionid = '%08x' % random.randrange(1 << 32)
                if self.sessionid not in ids:
                    break
            sid = self.sessionid
        else:
            sid = str(self.sessionid)
        if sessionSettings["store"]:
            #save the session variables back to file
            if not os.path.exists(sessionSettings["sessiondir"]):
                os.makedirs(sessionSettings["sessiondir"])
            path = sessionSettings["sessiondir"]+sid+sessionSettings["extension"]
            f = open(path,"wb")
            pickle.dump(self.sess, f)
            f.close()
        else:
            sessions[sid] = self.sess
        #set the sessionid in the user cookie
        response.set_cookie("sessionid", self.sessionid, secret=self.secret_key)
