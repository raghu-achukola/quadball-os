
function addListeners(){
    document.querySelectorAll('.game-element').forEach( 
        el => {
            console.log(el);
            el.addEventListener('click', function (e){
                gameId = this.getAttribute("destlink");
                window.open(`/possession-viewer/${gameId}`);

            })
        }
    )
}


fetch('/possession-html').then(response => response.text()).then(
    block =>{ 
        console.log(block);
        document.getElementById('game-dir').innerHTML = block;
        addListeners();
    }
)

