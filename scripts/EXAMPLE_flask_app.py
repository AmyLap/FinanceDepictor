from flask import Flask, render_template, request
import os
import json
import pandas as pd
import subprocess
import sys
# from source.datadog import DataDogLog
import time
from datetime import datetime, timedelta
import datetime as dt
import calendar

app = Flask(__name__)

def auth_user(user_email, department):
    dir_path = os.path.join(os.getcwd(), f'clients/')
    with open(f'{dir_path}/{department}/whitelist.json',"rb") as f:
        wl = json.load(f)
    if user_email in wl["all_access"] or not wl["all_access"]:
        return True
    else:
        return False

def read_config(config_path: str):
    with open(config_path, "rb") as j:
        config = json.load(j)
    return config

def write_config(config_path: str, config: dict):
    with open(config_path,"w") as cp:
        cp.write(json.dumps(config, indent=4))

@app.route('/')
def home():
    dir_path = os.path.join(os.getcwd(),'clients')
    res = os.listdir(dir_path)
    return render_template('index.html.jinja', department=res)

@app.route('/<department>')
def available_bots(department=None):
    user_email = request.headers.get('Cf-Access-Authenticated-User-Email')
    print('enter getJSONReuslt', flush=True)
    auth_user_bool = auth_user(user_email, department)
    if auth_user_bool:
        dir_path = os.path.join(os.getcwd(), 'clients')
        bots = [filename for filename in os.listdir(f'{dir_path}/{department}/') if os.path.isdir(os.path.join(f'{dir_path}/{department}/',filename))]
        return render_template("bots.html.jinja", department=department, bots=bots, user_email=user_email.split("@")[0].capitalize()) # type: ignore
    else:
        return render_template("unauthorized.html.jinja", department=department)

@app.route('/<department>/<bot_name>')
def run_bot(department=None, bot_name=None):
        
    user_email = request.headers.get('Cf-Access-Authenticated-User-Email')
    auth_user_bool = auth_user(user_email, department)
    config = read_config(str(os.getcwd()) + f"//clients//{department}//{bot_name}//config.json")

    if department == "Scheduled Bots":
        dd_config = config["datadog"]
        date = dt.datetime.utcnow()
        from_time = calendar.timegm(date.utctimetuple())*1000 -(86400*1000)
        to_time = calendar.timegm(date.utctimetuple())*1000
        return render_template("datadog.html.jinja",
                                bot_name=bot_name,
                                dept=department,
                                dd_source=dd_config["ddsource"], 
                                dd_service=dd_config["service"],
                                from_time=from_time,
                                to_time=to_time
                                )
    else:
        if auth_user_bool:
            config_path = str(os.getcwd()) + f"//clients//{department}//{bot_name}//config.json"
            
            config_ui = read_config(config_path)

            config = config_ui['user_input_config']

            config_ui['bot_config']['active_user'] = user_email

            with open(config_path,"w") as cp:
                cp.write(json.dumps(config_ui,indent=4))

            if "user_input" in config and config["user_input"]:
                user_input = config["user_input"]

                ui_input_map = {
                    "user_input":user_input,
                    "username" : False,
                    "drop_down":False,
                    "drop_down_header":False,
                    "drop_down_values":[],
                    "text_field" :False,
                    "text_area" : False,
                    "file_input" : False,
                    "text_field_name" : False,
                    "text_area_name" : False
                }

                for key,val in config.items():
                    if key in ui_input_map.keys():
                        ui_input_map[key] = val
            else:
                ui_input_map = {
                    "user_input":False
                }

            return render_template("running.html.jinja", 
                                    bot_name=bot_name, 
                                    department=department,
                                    ui_input_map=ui_input_map
                                    )

        else:
            return render_template("unauthorized.html.jinja", department=department)


@app.route('/<department>/<bot_name>/run', methods = ['POST',"GET"]) # type: ignore
def result(department=None,bot_name=None):
    if request.method == 'POST':
        date = dt.datetime.utcnow()
        from_time = calendar.timegm(date.utctimetuple())*1000 -(900*1000)
        to_time = calendar.timegm(date.utctimetuple())*1000
        
        result = request.form
        datadog = False

        config_path = str(os.getcwd()) + f"//clients//{department}//{bot_name}//config.json"
        bc = read_config(config_path)
        
        if "datadog" in bc.keys():
            datadog = True
            dd_config = bc["datadog"]

        if result:

            dir_path = os.path.join(os.getcwd(), f'clients/')
            # config_path = str(os.getcwd()) + f"//clients//{department}//{bot_name}//config.json"

            for i,v in result.items():
                bc["bot_config"][i] = v
            
            if "file_input" in bc['user_input_config'] and bc['user_input_config']['file_input'] and request.files['file_upload']:
                file = request.files['file_upload']
                new_file_path = os.path.join(dir_path, f'{department}/{bot_name}/{file.filename}')
                file.save(new_file_path)
                bc['bot_config']['document'] = file.filename

            # test = pd.read_excel(request.files(result['file_upload']))
            with open(config_path,"w") as cp:
                cp.write(json.dumps(bc,indent=4))

        # run python

        print_statements = None
        try:
            command = ['python3', f'clients/{department}/{bot_name}/main.py']

            test = subprocess.run(command, stdout=subprocess.PIPE)

            with open(config_path, "rb") as j:
                config_output = json.load(j)
                
            error = config_output['error_msg']
            
            print_statements = test.stdout.decode('utf-8')
            return_status = 0
        except Exception as e:
            return_status = 1
            error = e
        
        date = dt.datetime.utcnow()
        from_time = calendar.timegm(date.utctimetuple())*1000 -(900*1000)
        to_time = calendar.timegm(date.utctimetuple())*1000
        
        return render_template("result.html.jinja",
                                bot_name=bot_name,
                                output=return_status,
                                print_statements=print_statements,
                                error=error,
                                dd_source=None if not datadog else dd_config["ddsource"], # type: ignore
                                dd_service=None if not datadog else dd_config["service"], # type: ignore
                                datadog=datadog,
                                from_time=from_time,
                                to_time=to_time)

if __name__ == '__main__':
    app.run(debug=True, port=8080)