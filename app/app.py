# Import flask functions
from flask import Flask, render_template,request
import json
app = Flask(__name__)

TRANSLATION = {
    1:
    {'G':'Goal by {0}.',
    'GD':'Goal on the drive by {0}.',
    'GS':'Goal on the shot by {0}.',
    'OG':'Own Goal by {0}.',
    'E': 'Error by {0}.',
    'ET': 'Turnover penalty on {0}.',
    'EB': 'Blue card on {0} forces turnover.',
    'EY': 'Yellow card on {0} forces turnover.',
    'ER':'Red card on {0} forces turnover.',
    'EM':'Missed shot by {0}. Turnover.',
    'EP':'Errant pass by {0}. Turnover.',
    'ED':'Drop by {0}. Turnover.',
    'RCA':'Snitch catch by {0} is GOOD.',
    'OCA':'Snitch catch by {0} is GOOD.',
    '2CA':'Snitch catch by {0} is GOOD.',
    'RCB':'Snitch catch by {0} is GOOD.',
    'OCB':'Snitch catch by {0} is GOOD.',
    '2CB':'Snitch catch by {0} is GOOD.',
    'TB':'Beater {0} beats unkown chaser. Turnover.',
    'TBP':'Turnover forced by beater pressure by {0}.',
    'B':'blue card on {0}',
    'R': 'reset forced by {0}',
    'Y': 'yellow card on {0}',
    '2Y': 'second yellow card on {0}, {0} is ejected from the game',
    '1R': 'red card on {0},{0} is ejected from the game',
    'SOP':'SNITCH ON PITCH begins',
    'TIMEOUT':'TIMEOUT by {0}'
    },
    2:{
    'BU':'BROOMS UP! Quaffle Possession by {0}, Bludger Control by {1}',
    'G':'Goal by {0}, assist by {1}',
    'GD':'Goal on the drive by {0}, assist by {1}',
    'GS':'Goal on the shot by {0}, assist by {1}',
    'OG':'Own Goal',
    'GP':'{1} passes to {0} at the hoops, GOAL.',
    'T' :'Turnover by {0}',
    'TB':'Beat by {0} on {1} forces a TURNOVER.',
    'TBP':'Beater pressure by {0} on {1} forces a TURNOVER.',
    'TLB':'Bludger throw by {0} blocks shot/pass by {1}. Turnover',
    'TC':'Turnover forced by physical contact by {0} on {1}',
    'TL':'Shot by {1} blocked by {0}. Turnover.',
    'TD':'Pass between {1} defended by {0}. Turnover',
    'EP':'Errant pass from {0} in the direction of {1} . Turnover',
    'ED':'Pass by {1} dropped by {0}. Turnover'
    }
}

global POSSESSIONS,GAME_METADATA


def get_curr_possesions():
    return POSSESSIONS
def get_curr_metadata():
    return GAME_METADATA



@app.route('/')
def root(): 
    return render_template('index.html') 



@app.route('/metadata/<int:game_no>')
def get_metadata(game_no):
    global GAME_METADATA
    with open(f'data/{game_no}/game_metadata.json','r') as f: 
        GAME_METADATA = json.loads(f.read())
    
    return GAME_METADATA

@app.route('/possession-viewer/<int:game_no>')
def pview(game_no:int): 
    return render_template('possession_viewer.html',game_no = game_no) 




@app.route('/possessions/<int:game_no>')
def get_possessions(game_no:int):
    global POSSESSIONS

    with open(f'data/{game_no}/possessions.json','r') as f:
        POSSESSIONS = json.loads(f.read())


    response  = {
        'possessions':[
            {
                'data': poss,
                'description': describe_possession(poss)
            } for poss in POSSESSIONS
        ]
    }
    return response

# If we return json its like an API 
@app.route('/possession/<int:poss_no>')
def get_possession(poss_no:int):
    cp = get_curr_possesions()
    RESP =  {
        'data': cp[poss_no],
        'description': describe_possession(cp[poss_no])
    }
    print(RESP)
    return RESP

def describe_possession(poss_desc:dict):
    time_str = convert_time(poss_desc['time'])
    primary = poss_desc['primary']
    secondary = poss_desc['secondary']
    result = poss_desc['result']
    key = 2 if secondary else 1
    return f"{time_str} {TRANSLATION[key][result].format(primary,secondary)}"


def convert_time(gtime:int):
    return "" if gtime is None else "({:02d}:{:02d})".format(*divmod(gtime,60)) 
# If name is main, run flask 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)



    