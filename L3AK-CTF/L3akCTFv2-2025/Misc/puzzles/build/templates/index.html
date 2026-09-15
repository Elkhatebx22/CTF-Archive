<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
    <link rel="stylesheet" href="/css/styles.css">
    <script src="https://kit.fontawesome.com/081263bd39.js" crossorigin="anonymous"></script>
</head>

<body>
    <div class="content">
        <div class="header">
            <span><a href="/">Home</a></span>
            <span><a href="/help">Help</a></span>
            <span><a href="/puzzle">Play</a></span>
            <span><a href="/leaderboard">Leaderboard</a></span>
            <span class="username-link hide"><a href="/profile"></a></span>
        </div>
        <div class="body-container">
            <h1 class="puzzlesomg">Puzzles!</h1>
            <h3 class="puzzlesomg">paw-gress:</h3>
            <div class="level-progress" level="1">Level 1:<div class="progress-bar">
                    <div class="progress" style="width: 0%;"></div>
                </div><span class="max-needed"><span class="x">?</span>/<span class="y">?</span></span>
                <div class="reveal-flag noselect" onclick="getFlag(1)">Reveal Flag</div>
            </div>
            <div class="level-progress" level="2">Level 2:<div class="progress-bar">
                    <div class="progress" style="width: 0%;"></div>
                </div><span class="max-needed"><span class="x">?</span>/<span class="y">?</span></span>
                <div class="reveal-flag noselect" onclick="getFlag(2)">Reveal Flag</div>
            </div>
            <div class="level-progress" level="3">Level 3:<div class="progress-bar">
                    <div class="progress" style="width: 0%;"></div>
                </div><span class="max-needed"><span class="x">?</span>/<span class="y">?</span></span>
                <div class="reveal-flag noselect" onclick="getFlag(3)">Reveal Flag</div>
            </div>
            <div class="level-progress" level="4">Level 4:<div class="progress-bar">
                    <div class="progress" style="width: 0%;"></div>
                </div><span class="max-needed"><span class="x">?</span>/<span class="y">?</span></span>
                <div class="reveal-flag noselect" onclick="getFlag(4)">Reveal Code</div>
            </div>
            <div class="level-progress" level="5">Level 5:<div class="progress-bar">
                    <div class="progress" style="width: 0%;"></div>
                </div><span class="max-needed"><span class="x">?</span>/<span class="y">?</span></span>
                <div class="reveal-flag noselect" onclick="getFlag(5)">Reveal Flag</div>
            </div>
            <a href="/puzzle" class="play-link highlight">Play <i class="fa-solid fa-arrow-right"></i></a>
        </div>
    </div>
    <script>
        function setUsername() {
            let savedName = localStorage.getItem( "username" )
            if ( savedName != undefined && savedName != "" ) {
                document.querySelector( ".username-link > a" ).textContent = savedName
                document.querySelector( ".username-link" ).classList.remove( "hide" )
            }
        }

        async function loadProgressBars() {
            const response = await fetch( "/api/getsolves" )
            const data = await response.json()

            for ( let i = 0; i < data.n_levels; i++ ) {
                setProgressBar( i + 1, data.solves[ i ], data.required[ i ] )
            }
        }

        function setProgressBar( level, amount, required ) {
            let progressBar = document.querySelector( `.level-progress[level='${level}']` )
            let maxNeeded = progressBar.querySelector( ".max-needed" )
            maxNeeded.querySelector( ".x" ).textContent = `${amount}`
            maxNeeded.querySelector( ".y" ).textContent = `${required}`

            let percentDone = Math.min( amount / required, 1 ) * 100
            progressBar.querySelector( ".progress" ).style.width = `${percentDone}%`

            if ( amount >= required ) {
                progressBar.querySelector( ".reveal-flag" ).classList.remove( "noselect" )
                progressBar.querySelector( ".reveal-flag" ).classList.add( "clickme" )
            } else {
                progressBar.querySelector( ".reveal-flag" ).classList.add( "noselect" )
            }
        }

        function getFlag( level ) {
            let progressBar = document.querySelector( `.level-progress[level='${level}']` )
            let progress = progressBar.querySelector( ".progress" )
            let revealFlag = progressBar.querySelector( ".reveal-flag" )

            if ( revealFlag.classList.contains( "noselect" ) ) {
                return
            }
            fetch( '/api/getflag', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify( {
                    level: level - 1
                } ),
            } ).then( response => response.json() ).then( data => {
                revealFlag.classList.remove( "clickme" )
                if ( data.error != undefined ) {
                    progress.style.color = "red"
                    progress.textContent = data.error
                } else {
                    progress.style.color = ""
                    progress.classList.add( "reversed" )
                    progress.style.width = "0%"
                    setTimeout( () => {
                        progress.style.background = "#df4194"
                        progress.innerHTML = data.flag
                        progress.style.width = "100%"
                        progressBar.querySelector( ".reveal-flag" ).classList.add( "noselect" )
                        progressBar.querySelector( ".reveal-flag" ).style.background = "#df4194"
                    }, 500 )
                }
            } )
                .catch( error => {
                    console.error( error );
                } );
        }

        setUsername()
        loadProgressBars()

    </script>
</body>

</html>