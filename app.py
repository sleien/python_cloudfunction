from flask import Flask, request
import json
import yaml
import os
from dotenv import load_dotenv
import hmac, hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()
ADMIN_SECRET = os.getenv('ADMIN_SECRET')
config = []
scheduler = BackgroundScheduler()


app = Flask(__name__)
app.config["DEBUG"] = os.getenv('DEBUG') 

@app.route("/<function>")
def dyn_function(function):
    item = next(item for item in config if item["endpoint"] == function)
    if(not item):
        return "{'message': 'endpoint not found'}", 404
    exec("import functions." + item["file"].split(".",1)[0])
    return eval("functions." + item["file"].split(".",1)[0] + ".main()")


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

def cron_executer(function_name):
    exec("import functions." + function_name)
    eval("functions." + function_name + ".main()")

def init():
    global config
    new_config = []
    for filename in os.listdir("configs"):
        f = os.path.join("configs", filename)
        configs = yaml.safe_load(open(f))
        for e in configs:
            if e["endpoint"]:
                new_config.append(e)
            if e["cron"]:
                scheduler.add_job(lambda: cron_executer(e["file"].split(".",1)[0]), CronTrigger.from_crontab(e["cron"]))
    config = new_config
    return True

init()
scheduler.start()
app.run()