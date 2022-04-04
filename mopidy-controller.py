class Plugin:
    name = "Mopidy"
    author = "marios8543"

    main_view_html = """
    <html>
        <head>
            <style>
                li {
                    color: #dcdedf;
                    border-top: 1px solid #dcdedf;
                    padding-top:3px;
                    margin-bottom:3px;
                    list-style-position:inside;
                }
            </style>
            <script src="/static/library.js"></script>
        </head>
        <body>
            <div style="width:100%; text-align: center;">
                <button onclick="showing_playlists = false;" style="display:inline-block; border-radius: 100px; background: #23262e; color: #dcdedf;">
                Track List
                </button>
                <button onclick="set_playlists()" style="display:inline-block; border-radius: 100px; background: #23262e; color: #dcdedf;">
                Playlists
                </button>
            </div>
        
            <ul id="playlist" style="list-style-type:none; padding: 0; overflow-y: scroll; height:85%;"></ul>
            <script>
                var showing_playlists = false;

                async function call_mopidy_rpc(command, params = {}) {
                    let res = await fetch_nocors('http://localhost:6680/mopidy/rpc', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ "jsonrpc": "2.0", "id": 1, "method": command, "params": params }),
                    });
                    return JSON.parse(res.body).result;
                }

                async function set_playlists() {
                    showing_playlists = true;
                    let playlists = await call_mopidy_rpc("core.playlists.as_list");
                    document.getElementById("playlist").innerHTML = "";
                    playlists.forEach(el => {
                        let e = document.createElement("li");
                        e.innerText = el.name;
                        e.onclick = async function() {
                            await call_mopidy_rpc("core.tracklist.clear");
                            let songs = await call_mopidy_rpc("core.playlists.get_items", {"uri" : el.uri});
                            let uris = []
                            songs.forEach(song => uris.push(song.uri));
                            await call_mopidy_rpc("core.tracklist.add", {"uris" : uris});
                            await call_mopidy_rpc("core.playback.play");
                        }
                        document.getElementById("playlist").appendChild(e);
                    });
                }

                setInterval(async function () {
                    if (showing_playlists) return;
                    let tracklist = await call_mopidy_rpc("core.tracklist.get_tl_tracks");
                    document.getElementById("playlist").innerHTML = "";
                    tracklist.forEach(el => {
                        let e = document.createElement("li");
                        e.innerText = `${el.track.artists != undefined ? el.track.artists[0].name : "Unknown artist"} - ${el.track.name}`;
                        e.onclick = function() {
                            call_mopidy_rpc("core.playback.play", {"tlid" : el.tlid});
                        }
                        document.getElementById("playlist").appendChild(e);
                    });
                }, 1000);
            </script>
        </body>
    </html>
    """

    tile_view_html = """
    <div class="quickaccesscontrols_PanelSectionRow_26R5w" style="background: #23262e; border-radius: 5px;">
        <div style="display: inline-block;">
            <div id="current_artist">Nothing playing</div>
            <div id="current_song"></div>
        </div>
        <div style="width:100%; text-align: center;">
            <button id="mopidy_btn_prev" style="display:inline-block; border-radius: 100px; background: #23262e; color: #dcdedf;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-left-fill" viewBox="0 0 16 16">
                    <path d="m3.86 8.753 5.482 4.796c.646.566 1.658.106 1.658-.753V3.204a1 1 0 0 0-1.659-.753l-5.48 4.796a1 1 0 0 0 0 1.506z"/>
                </svg>
            </button>
            <button id="mopidy_btn_play" style="display:inline-block; border-radius: 100px; background: #23262e; color: #dcdedf;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
                </svg>
            </button>
            <button id="mopidy_btn_next" style="display:inline-block; border-radius: 100px; background: #23262e; color: #dcdedf;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-right-fill" viewBox="0 0 16 16">
                    <path d="m12.14 8.753-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"/>
                </svg>
            </button>
        </div>
    </div>
    <script>
        const MUSIC_ICON_SVG = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-music-note" viewBox="0 0 16 16">
                <path d="M9 13c0 1.105-1.12 2-2.5 2S4 14.105 4 13s1.12-2 2.5-2 2.5.895 2.5 2z"/>
                <path fill-rule="evenodd" d="M9 3v10H8V3h1z"/>
                <path d="M8 2.82a1 1 0 0 1 .804-.98l3-.6A1 1 0 0 1 13 2.22V4L8 5V2.82z"/>
            </svg>
        `;

        const PLAY_ICON = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">
            <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
        </svg>
        `

        const PAUSE_ICON = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">
            <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"/>
        </svg>
        `

        async function call_mopidy_rpc(command, params = {}) {
            let res = await fetch_nocors('http://localhost:6680/mopidy/rpc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "jsonrpc": "2.0", "id": 1, "method": command, "params": params }),
            });
            return JSON.parse(res.body).result;
        }

        document.getElementById("mopidy_btn_prev").onclick = function(e) {
            console.log("prev")
            e.stopPropagation();
            call_mopidy_rpc("core.playback.previous");
        }

        document.getElementById("mopidy_btn_play").onclick = async function (e) {
            e.stopPropagation();
            let playback_state = await call_mopidy_rpc("core.playback.get_state");
            if (playback_state.toLowerCase() == "paused") 
                call_mopidy_rpc("core.playback.resume");
            else if (playback_state.toLowerCase() == "playing") 
                call_mopidy_rpc("core.playback.pause");
        }

        document.getElementById("mopidy_btn_next").onclick = function(e) {
            e.stopPropagation();
            call_mopidy_rpc("core.playback.next");
        }

        function set_current_song(title, artist) {
            document.getElementById("current_song").innerText = title;
            document.getElementById("current_artist").innerText = artist;
        }

        setInterval(async function () {
            let current_song = await call_mopidy_rpc("core.playback.get_current_track");
            if (current_song) set_current_song(current_song.name, current_song.artists[0].name);

            let playback_state = await call_mopidy_rpc("core.playback.get_state");
            if (playback_state.toLowerCase() == "paused") document.getElementById("mopidy_btn_play").innerHTML = PLAY_ICON;
            else if (playback_state.toLowerCase() == "playing") document.getElementById("mopidy_btn_play").innerHTML = PAUSE_ICON;
        }, 1000);
    </script>
    """