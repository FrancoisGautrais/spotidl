
function modal_alert(title, content=""){
    $("#alert-title").html(title)
    $("#alert-content").html(content)
    $("#alert-modal").modal("show")
}

var MODAL_CALLBACK={
}

function modal_call(name, args=[]){
    var fct = MODAL_CALLBACK[name];
    if(fct){
        fct.apply(args);
    }
}

function set_modal_callback(name, fct=null){
    MODAL_CALLBACK[name]=fct
}

function modal_download(n, download_all, download_select){
    set_modal_callback('download_all', download_all)
    set_modal_callback('download_select', download_select)
    $("#download-n-tracks").html(n+"")
    $("#download-modal").modal("show")
}


function confirm(title, message, on_yes, on_no=null){
    set_modal_callback('confirm_yes', on_yes)
    set_modal_callback('confirm_no', on_no)
    $("#confirm-title").html(title)
    $("#confirm-content").html(message)
    $("#confirm-modal").modal("show")
}

function itof(x, f){
    var factor=Math.pow(10, f)
    return Math.ceil(x*factor)/factor
}

function notification_close(not){
    not.remove()
}

function toast(html, duration=5000){
    var host = $(".notifications-host")
    var id = "notificationid-"+Date.now()
    var not = $('<div class="notification notification-info" id="'+id+'" onclick="notification_close($(this))">'+html+'</div>')
    host.append(not)
    if(duration>0){
        setTimeout(function(){
            notification_close(not)
        }, duration);
    }
}

function toast_error(html){
    var host = $(".notifications-host")
    var id = "notificationid-"+Date.now()
    var not = $('<div class="notification notification-error" id="'+id+'" onclick="notification_close($(this))">'+html+'</div>')
    host.append(not)
}

function toast_warning(html, duration=60000){
    var host = $(".notifications-host")
    var id = "notificationid-"+Date.now()
    var not = $('<div class="notification notification-warning" id="'+id+'" onclick="notification_close($(this))">'+html+'</div>')
    host.append(not)
    if(duration>0){
        setTimeout(function(){
            notification_close(not)
        }, duration);
    }
}


function process_input_track(track){
    if(track){
        return Object.assign(track,{
            duration: Utils.formatDurationHMS(track.duration),
            artist: (track.artists)?track.artists[0].name:"none"
        })
    }else{
        return {
            url: "none",
            name : "none",
            duration : "-",
            artist : "none",
            artists : [],
            album : "none",
            track_number : "-",
            class: "hidden"
        }
    }
}

function process_input_track_spotify(track){
    var dur = track.duration;
    if(!dur) dur=track.duration_ms/1000;
    if(track){
        return {
            duration: Utils.formatDurationHMS(dur),
            artist: track.artists[0].name,
            artists : artists_cat(track.artists),
            url: track.external_urls.spotify,
            id: track.id,
            name: track.name,
            track_number: "",
            calss: ""
        }
    }else{
        return {
            url: "none",
            name : "none",
            duration : "-",
            artist : "none",
            artists : [],
            album : "none",
            track_number : "-",
            class: "hidden"
        }
    }
}

function artists_cat(artists){
    var names = []
    for(var i in artists)
        names.push(artists[i].name)
    return names.join(" & ")
}

function process_input_album(album){
    return {
        "artists" : artists_cat(album.artists),
        "date" : album.release_date.substr(0,4),
        "name" : album.name,
        "url" : album.external_urls.spotify,
        "id" : album.id,
        "total_tracks" : album.total_tracks
    }
}

function process_input_artist(a){
    return {
        "image" : (a.images && a.images.length)?a.images[0].url:"",
        "name" : a.name,
        "url" : a.external_urls.spotify,
        "id" : a.id,
    }
}

function openInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}

function process_input_tracks_array(tracks, spot=false){
    for(var i in tracks){
        tracks[i]=spot?process_input_track_spotify(tracks[i]):process_input_track(tracks[i]);
        tracks[i].index=i;
    }
    return tracks
}

function process_input_albums_array(albums){
    for(var i in albums){
        albums[i]=process_input_album(albums[i])
    }
    return albums
}

function process_input_artists_array(albums){
    for(var i in albums){
        albums[i]=process_input_artist(albums[i])
    }
    return albums
}

class Loading {

    static depth=0;
    static open(text="Chargement, merci de patienter"){
        $(".loading-text").html(text)
        $("#loading-host").show()
        Loading.depth++;
    }

    static close(){
        Loading.depth--;
        if(Loading.depth<0) Loading.depth=0;
        if(!Loading.depth)
            $("#loading-host").hide()
    }

}