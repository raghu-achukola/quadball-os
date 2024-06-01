var gameNumber = document.getElementById('gameNumber')
var possViewer = document.getElementById('possession-viewer')
var description = document.getElementById('description-header')
var team1Name = document.getElementById('team-one')
var team2Name = document.getElementById('team-two')
var team1Score = document.getElementById('score-one')
var team2Score = document.getElementById('score-two')
var possNumber = document.getElementById('possession-number')
var POSSESSIONS = [];

// Unique to the particular url we are on: 
// ROOT/{game_no} 
var filmID = '';
var gameNo = gameNumber.innerText

// Zero Padding
Number.prototype.pad = function(size) {
    var s = String(this);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
}

var TEAMS = {}
var videotime = 0;
var switchTime = 0;
var runningScore = {"-1": [0,0]};
var player;
function displayPossession(possNo,forceSeek){
    console.log(`displayPossession called with possNo ${possNo}`)

    data = POSSESSIONS[possNo]
    console.log(data);
    description.innerHTML = data.description
    updateScore(possNo,data)
    console.log(runningScore)
    setGametime(data.data.time)
    if (forceSeek){
        seek(data.data.film_timestamp)
    }
    switchTime = POSSESSIONS[possNo+1].data.film_timestamp
    console.log(`Next Possession starts @: ${switchTime}`)

}
function displayTeams(team1,team2){
    team1Name.innerText = team1;
    team2Name.innerText = team2;
}
function setGametime(time){
    let min =  Math.floor(time/60);
    let sec = time % 60 ;
    gametime.innerText = `(${min.pad(2)}:${sec.pad(2)})`
    
}

function updateScore(possNo,data){
    possNumber.innerText = `P #${possNo+1}`
    if (possNo in runningScore){
        scores = runningScore[possNo]
        setScore(scores[0],scores[1])
    }
    else{
        oldScores = runningScore[possNo-1]
        let offense = data.data.offense
        let newTeamsScore = [oldScores[0],oldScores[1]]
        newTeamsScore[TEAMS[offense]] = newTeamsScore[TEAMS[offense]] + (data.data.result[0]=='G'? 10:0)
        runningScore[possNo] = newTeamsScore
        console.log(`Offense: ${offense} - New Score: ${newTeamsScore}`)
        setScore(newTeamsScore[0],newTeamsScore[1])
    }
}

function setScore(team1,team2){
    team1Score.innerText = team1
    team2Score.innerText = team2
}

function shiftPossession(delta,forceSeek = false){
    let currPoss = parseInt(possViewer.getAttribute('currPoss'))
    newPoss = currPoss+delta
    displayPossession(newPoss,(newPoss==0) || forceSeek)
    possViewer.setAttribute('currPoss',currPoss+delta)

}



// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
function onYouTubeIframeAPIReady() {
    console.log('gdi');
    player = new YT.Player('display', {
        // height: '390',
        // width: '640',
        videoId: filmID,
        host: 'http://www.youtube-nocookie.com',
        playerVars: {
        'playsinline': 1,
        'start':1,
        'enablejsapi':1,
        'controls':0
        },
        events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
        }
    });
    
    fetch(`/metadata/${gameNo}`).then(
        (response) => (response.json())
    ).then(
        (metadata) => { 
            TEAMS[metadata.team_a_name] = 0;
            TEAMS[metadata.team_b_name] = 1;
            filmID = metadata.film_id
            console.log(filmID)
            displayTeams(metadata.team_a_name,metadata.team_b_name);
            changeVideo(filmID)
        }
    )
}
function onPlayerReady(evt){
    console.log(evt)
    player.loadVideoById(filmID)
    console.log(player.getCurrentTime())
    console.log('opr');
    function updateTime() {
        var oldTime = videotime;
        if(player && player.getCurrentTime) {
            videotime = player.getCurrentTime();
        }
        if(videotime !== oldTime) {
            onProgress(videotime);
        }
    }
    timeupdater = setInterval(updateTime, 100);
    document.getElementById('display').setAttribute('min-width', '100%')
}
function onPlayerStateChange(evt){
    console.log('opsc');  
    console.log(evt)
    console.log(player.getCurrentTime());
}
function seek(seconds){
    if(player){
        player.seekTo(seconds, true);
    }
}

function onProgress(currentTime) {
    if (currentTime > switchTime){
        console.log("NEW POSS")
        shiftPossession(1,false)
    }
}
  
function changeVideo(videoId){
    player.cueVideoById(videoId)
}


fetch(`/possessions/${gameNo}`).then((response)=> (response.json())).then(
    (data) => {
        POSSESSIONS = data.possessions;
        console.log(POSSESSIONS)
        loadYoutubeIframe()
    }
)

// Button Listeners
function loadYoutubeIframe(){
    console.log('loadYoutubeIframe called')
    let leftButton = document.getElementById('left-button')
    leftButton.addEventListener('click',(ev) => shiftPossession(-1,true))
    let rightButton = document.getElementById('right-button')
    rightButton.addEventListener('click',(ev) => shiftPossession(1,true))
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}