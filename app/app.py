# Import flask functions
from flask import Flask, render_template,request
import json
import boto3
import os
import re 
BUCKET = os.environ['QUADBALL_DATA_LAKE_BUCKET']
POSSESSION_PREFIX = 'possessions/hydrated'
METADATA_PREFIX = 'game-metadata'
GAME_DESC_PATTERN = r'\((.*)\)\s*\[(.*)\]\s*(.*)'
app = Flask(__name__)
s3 = boto3.client('s3')

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



def s3_get_possessions(game_no:int):
    resp = s3.get_object(Bucket = BUCKET, Key = f'{POSSESSION_PREFIX}/{game_no}.json')
    json_str = resp['Body'].read().decode('utf-8')
    return json.loads(json_str)

@app.route('/metadata/<int:game_no>')
def s3_get_metadata(game_no:int):
    resp = s3.get_object(Bucket = BUCKET, Key = f'{METADATA_PREFIX}/{game_no}.json')
    json_str = resp['Body'].read().decode('utf-8')
    metadata =  json.loads(json_str)
    metadata |= determine_film_source(metadata.get('film_links',''))
    return metadata


@app.route('/')
def root(): 
    return render_template('index.html') 


def determine_film_source(film_link:str) -> dict:
    info = {}
    youtube =  link_is_youtube(film_link)
    if film_link and youtube:
        info['video_site'], info['film_id'] = youtube.groups()
    return info

def link_is_youtube(film_link:str): 
    YOUTUBE_PATTERN = r'.*(youtube)[.]com\/watch\?v\=([A-z0-9\-\_]+)'
    return re.match(YOUTUBE_PATTERN,film_link)


@app.route('/possession-html')
def get_game_html() :
    desc =   s3.get_object(Bucket = BUCKET, Key = 'db/game_descriptions.csv')['Body'].read().decode('utf-8')
    output = ''
    for row in desc.split('\n')[1:]:
        if not row.strip():
            continue
        _id,description = row.strip().split(',')
        season, game_desc, result = re.match(GAME_DESC_PATTERN,description).groups()
        output+=render_template('game_row.html',_id = _id, game_desc = game_desc, season= season, result = result)
    return output

@app.route('/possession-viewer')
def game_viewer():
    return render_template('game_dir.html')



@app.route('/possession-viewer/<int:game_no>')
def pview(game_no:int): 
    return render_template('possession_viewer.html',game_no = game_no) 



@app.route('/possessions/<int:game_no>')
def get_possessions(game_no:int):

    POSSESSIONS = s3_get_possessions(game_no=game_no)

    response  = {
        'possessions':[
            {
                'data': poss,
                'description': describe_possession(poss)
            } for poss in POSSESSIONS
        ]
    }
    return response

# # If we return json its like an API 
# @app.route('/possession/<int:game_no>/<int:poss_no>')
# def get_possession(game_no:int,poss_no:int):
#     cp = get_curr_possesions()
#     if not cp: 
#         cp = get_possessions(game_no)
#     RESP =  {
#         'data': cp[poss_no],
#         'description': describe_possession(cp[poss_no])
#     }
#     print(RESP)
#     return RESP

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



    