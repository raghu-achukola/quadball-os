{{  config( materialized = 'table') }}

select game_id, 
'' as possession_number,
possession:extras::array  as extras,
possession:film_timestamp as film_timestamp,
possession:offense::string as offense, 
possession:result::string as result,
possession:primary::array as primary_players, 
possession:secondary::array as secondary_players, 
possession:time::int as gametime_seconds
from {{source('staging','possessions')}}