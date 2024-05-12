from enum import Enum
import re
import json
from dataclasses import dataclass


def enumify(cls):

    class ExtraParser(cls):
        _REGEX = {
            ExtraKind.OVERALL : '()()',
            ExtraKind.TEAM_EXTRA: '(A|B)()',
            ExtraKind.DEFENSE_EXTRA: '()([0-9]+)',
            ExtraKind.OFFENSE_EXTRA: '()([0-9]+)',
            ExtraKind.PLAYER_EXTRA: '(A|B)([0-9]+)'
        }
        def __init__(self):
            definition = {}
            kind_dic = {}
            for attribute in self.__dir__():
                if not attribute.startswith('_'):      # ignore natural 'dunder' methods
                    string,kind = getattr(self,attribute)
                    definition[string] = attribute
                    kind_dic[kind] = kind_dic.get(kind,[]) + [string]
            self.definition,self.kind_dic = definition,kind_dic
            self._REGEX_PATTERNS = {
                kind: f"({'|'.join(extra_strings)}){self._REGEX.get(kind)}" 
                for kind, extra_strings in self.kind_dic.items()
            }
            
            self.massive_regex_string = '|'.join([v for v in self._REGEX_PATTERNS.values()])
            
        def _get_def(self,ex:str):
            return getattr(self,self.definition.get(ex))

    return ExtraParser


class ExtraKind(Enum):
    OVERALL = 0
    TEAM_EXTRA = 1
    PLAYER_EXTRA = 2
    DEFENSE_EXTRA = 3
    OFFENSE_EXTRA = 4



@enumify
class ExtraType:
    YELLOW_CARD = ('Y',ExtraKind.PLAYER_EXTRA)
    SECOND_YELLOW_CARD = ('2Y',ExtraKind.PLAYER_EXTRA)
    SECOND_YELLOW_RED_CARD = ('2YR',ExtraKind.PLAYER_EXTRA)
    THIRD_YELLOW_RED_CARD = ('3YR',ExtraKind.PLAYER_EXTRA)
    STRAIGHT_RED_CARD = ('1R',ExtraKind.PLAYER_EXTRA)
    BLUE_CARD = ('B',ExtraKind.PLAYER_EXTRA)
    FORCED_RESET = ('R',ExtraKind.DEFENSE_EXTRA)
    FORCED_RESET_BY_A_CHASER = ('RC',ExtraKind.DEFENSE_EXTRA)
    UNFORCED_RESET = ('UR',ExtraKind.OFFENSE_EXTRA)
    FLAG_CATCH = ('C',ExtraKind.PLAYER_EXTRA)
    TIMEOUT = ('TO',ExtraKind.TEAM_EXTRA)
    FLAG_ON_PITCH = ('S',ExtraKind.OVERALL)

class Extra:
    TYPE_CHECKER = ExtraType()
    def __init__(self,extra_type:ExtraType,team:str,player:tuple):
        self.extra_type,self.team,self.player = extra_type,team,player

    def from_string(extra:str):
        result_kind = None
        for kind, pattern in Extra.TYPE_CHECKER._REGEX_PATTERNS.items():
            match = re.match(pattern,extra)
            if match:
                result_kind = kind
                break
        assert result_kind or match, f'Could not match extra {extra} to an established pattern'
        extra_type, team, player_number = match.groups()
        return Extra(
            extra_type = Extra.TYPE_CHECKER.definition[extra_type],
            team = team,
            player = (team, player_number) if str(player_number) else None
        )
    
    def copy(self):
        return Extra(self.extra_type,self.team,self.player)

    def to_dict(self:str):
        return {
            'extra_type': str(self.extra_type),
            'team': self.team if self.team else None ,
            'player': list(self.player) if type(self.player) == tuple else self.player
        }
    
    def to_json(self:str):
        return json.dumps(self.to_dict())




class PossessionResult(Enum):
    G = 1                 # Goal. All goals have the goalscorer as the primary, assist as the secondary
    E = 2                 # Generic Error. Error is an unforced turnover. The person who commited the mistake
                          # described in the error is the primary, associated parties are the secondary
    T = 3               # Turnover FORCED. The DEFENDER(s) who forced the turnover are the primary
    GD = 4
    GP = 5
    GS = 6
    EM = 7
    EP = 8
    ED = 9
    EF = 10
    ET = 11
    EB = 12
    EY = 13
    E2Y = 14
    E2YR = 15
    E3YR = 16
    ER = 17

    TC = 18
    TD = 19
    TB = 20
    TBP = 21
    TL = 22

                

class ExtraKind(Enum):
    OVERALL = 0
    TEAM_EXTRA = 1
    PLAYER_EXTRA = 2
    DEFENSE_EXTRA = 3
    OFFENSE_EXTRA = 4





class StatSheetPossession:
    def __init__(self,extras:list[Extra],offense:str,time:int,result:PossessionResult, primary:list, secondary:list):
        self.extras,self.offense,self.time,self.result,self.primary,self.secondary = extras,offense,time,result,primary,secondary
        self.defense = 'A' if offense == 'B' else 'B'
    
    def copy(self):
        return StatSheetPossession(
            extras = [ex.copy() for ex in self.extras] if self.extras else None,
            offense=self.offense,
            time = self.time,
            result= self.result,
            primary = self.primary.copy() if self.primary else None,
            secondary = self.secondary.copy() if self.secondary else None
        )

    def parse_extras(extras:str, offense:str, defense:str) -> list[Extra]:
        extras = extras.split(',')
        extra_list = []
        for extra in extras: 
            ex = Extra.from_string(extra)
            if getattr(ExtraType,ex.extra_type)[1].value == ExtraKind.DEFENSE_EXTRA.value:
                ex.team = defense
                ex.player = (defense, ex.player[1])
                print('ooh')
            elif getattr(ExtraType,ex.extra_type)[1] is ExtraKind.OFFENSE_EXTRA:
                ex.team = offense
                ex.player = (offense, ex.player[1])
                print('aah')
            extra_list.append(ex)
        return extra_list
    
    def parse_timestring(timestring:str) -> int:
        assert timestring.isnumeric() and len(timestring) == 4, f'Timestring {timestring} is improperly formatted'
        return int(timestring[:2])*60 + int(timestring[2:])

    def get_players(player_cell:str, team:str)-> list[tuple]:
        return [(team,player_num) for player_num in player_cell.split(',')] if player_cell else None


    def from_values(extras:str, offense:str, time_string:str, result:str, primary:str, secondary:str): 
        defense = 'A' if offense == 'B' else 'B'
        extra_list = StatSheetPossession.parse_extras(extras,offense=offense,defense=defense) if extras else None
        gametime = StatSheetPossession.parse_timestring(time_string) if time_string else None
        poss_result = PossessionResult[result]
        if result in ('RCA','CA','OCA','2CA'):
            primary_team ='A'
            secondary_team = None
        elif result in ('RCB','CB','OCB','2CB'):
            primary_team ='B'
            secondary_team = None
        elif result == 'OG':
            primary_team = offense
            secondary_team = None
        elif result.startswith('G') or result.startswith('E'):
            primary_team, secondary_team = offense,offense
        elif result.startswith('T'):
            primary_team,secondary_team = defense,offense
        else:
            pass
        primary_list = StatSheetPossession.get_players(primary,primary_team)
        secondary_list = StatSheetPossession.get_players(secondary,secondary_team)
        return StatSheetPossession(
            extras=extra_list,
            offense=offense,
            time=gametime,
            result=poss_result,
            primary=primary_list,
            secondary=secondary_list
        )

    def to_json(self, **kwargs): 
        return json.dumps({
            'extras': None if self.extras is None else [extra.to_dict() for extra in self.extras],
            'offense': self.offense ,
            'time': self.time,
            'result': None if self.result is None else self.result.name,
            'primary': None if self.primary is None else [list(player) if type(player)== tuple else player  for player in self.primary],
            'secondary':None if self.secondary is None else [list(player) if type(player) == tuple else player for player in self.secondary]
        }, **kwargs)
        

@dataclass
class StatSheetMetadata:
    season_id: str
    game_id: int
    tournament_id:int
    team_a_name:str
    team_a_id:int
    team_b_name:str
    team_b_id:int
    film_links:str


class StatSheetRoster:

    def from_dict(player_dict): 
        new = StatSheetRoster()
        new.player_dict = player_dict
        new.by_name = {}
        new.by_id = {}
        new.by_team = {}

        for key, values in player_dict.items():
            team,num = key
            name = values['name']
            id = values['id']
            new.by_name[key] = name
            new.by_id[key] = id
        return new

    def __getitem__(self, val):
        if type(val) == tuple:
            #TODO: oof
            team,pl = val
            return self.player_dict[(team,int(pl))]
        elif type(val) == str:
            #TODO: replace with regex match
            if '-' in val:
                team, num = val.split('-')
                return self.__getitem__((team,int(num)))
            elif val in ('A','B'):
                return {
                    jersey: value for (team,jersey), value in self.player_dict.items()
                    if team == val
                }
        
    def __call__(self, type:str):
        assert type in ('name','id')
        if type == 'name':
            return StatSheetRoster.from_dict(self.by_name)
        elif type == 'id':
            return StatSheetRoster.from_dict(self.by_id)
        




# roster['A']['6']['id']
# roster('A')['6']['id']
# roster('id')['A']['6']

