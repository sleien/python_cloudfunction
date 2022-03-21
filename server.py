from flask import Flask
from flask import request
import json, yaml, os
from dotenv import load_dotenv
import hmac, hashlib

load_dotenv()
ADMIN_SECRET = os.getenv('ADMIN_SECRET')
config = {}


app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/<function>")
def dyn_function(function):
    ex_locals={}
    item = next(item for item in config["functions"] if item["endpoint"] == function)
    if(not item):
        return "{'message': 'endpoint not found'}", 404
    exec("import " + item["file"].split(".",1)[0])
    return eval(item["file"].split(".",1)[0] + ".main()")


@app.route("/admin/reload",  methods = ['POST'])
def reload():
    if(not validate_signature(request, ADMIN_SECRET)):
        return "{'message':'incorrect secret'}", 401
    
    if init():
        return "{'message': 'reinitialized'}", 200
    else:
        return "{'message': 'reinitialization failed'}",500
     

def validate_signature(payload, secret):

    # Get the signature from the payload
    signature_header = payload.headers.get("X-Hub-Signature-256")
    sha_name, github_signature = signature_header.split('=')
    if sha_name != 'sha256':
        print('ERROR: X-Hub-Signature in payload headers was not sha256=****')
        return False
      
    # Create our own signature
    body = bytes(json.dumps(payload.get_json()),'utf-8')
    byte_secret = bytes(secret, "utf-8")
    local_signature = hmac.new(byte_secret, msg=body, digestmod=hashlib.sha256)

    # See if they match
    print(local_signature.hexdigest())
    print(github_signature)
    return hmac.compare_digest(local_signature.hexdigest(), github_signature)

def init():
    global config
    config = yaml.safe_load(open(os.getcwd() + '/config.yaml'))
    return True

init()
app.run()