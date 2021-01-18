
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
    return not;
}

function toast_error(html){
    var host = $(".notifications-host")
    var id = "notificationid-"+Date.now()
    var not = $('<div class="notification notification-error" id="'+id+'" onclick="notification_close($(this))">'+html+'</div>')
    host.append(not)
    return not;
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
    return not;
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
            calss: "",
            album: track.album.name,
            year: track.album.release_date.substring(0,4),
            uuid: track.uuid,
            album_uuid: track.album_uuid,
            artist_uuid: track.artist_uuid,
            state: track.state,
            error: track.error
        }
    }else{
        return {
            url: "none",
            name : "none",
            duration : "-",
            artist : "none",
            artists : [],
            album : "none",
            album : "0",
            track_number : "-",
            class: "hidden",
            uuid: "undefined",
            album_uuid: "undefined",
            artist_uuid: "undefined",
            state: "undefined",
            error: "undefined"
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
        console.log("track = ", tracks[i])
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

function isObject(obj) {
  return obj === Object(obj) && !Array.isArray(obj);
}

function dict_compare(d1, d2){
    if(d1.length!=d2.length){
        return false;
    }
    for(var key in d1){
        if(isObject(d1[key]) && isObject(d2[key])){
            if(!dict_compare(d1[key], d2[key]))
                return false
        }else if(Array.isArray(d1[key]) && Array.isArray(d2[key])){
            if(!dict_compare(d1[key], d2[key]))
                return false
        }else if(d1[key]!=d2[key]){
            return false
        }
    }
    return true
}


class Application{
    constructor(){
        this.params = Application.parse_query_string(window.location.search.substring(1))
        this._is_init=false;//template
        this._is_loaded=false; //load
        this._to_load={}
        this._ready=[]
    }

    call_ready(){
        for(var k in this._ready){
            this._ready[k]()
        }
    }

    ready(fct){
        this._ready.push(fct)
    }

    finished(id){
        delete this._to_load[id];
        if(!this._to_load.length){
            this._is_loaded=true;
            this.call_ready()
        }
    }

    enqueue_to_load(x, id){
        if(this._is_init){
            x();
        }else{
            this._to_load[id]=x
        }
    }

    on_template_init(){
        this._is_init=true;
        for(var id in this._to_load){
            this._to_load[id]();
        }
    }

    static parse_query_string(query) {
        if(query=="") return {}
        var vars = query.split("&");
        var query_string = {};
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            var key = decodeURIComponent(pair[0]);
            var value = decodeURIComponent(pair[1]);
            // If first entry with this name
            if (typeof query_string[key] === "undefined") {
              query_string[key] = decodeURIComponent(value);
              // If second entry with this name
            } else if (typeof query_string[key] === "string") {
              var arr = [query_string[key], decodeURIComponent(value)];
              query_string[key] = arr;
              // If third or later entry with this name
            } else {
              query_string[key].push(decodeURIComponent(value));
            }
        }
        return query_string;
    }

}
var App = new Application();

Template.ready(function(){
    App.on_template_init();
})



class MenuWidget {
    constructor() {
        var self = this;
        this.overlay=$('<div class="menu-overlay hidden"></div>')
        this.host=$('<div class="menu-host hidden"></div>')
        this.menu_trigger=$(".menu-icon")
        this.host.append($(".root-menu"))

        this.overlay.on("click", function(){
            self.toggle();
        })
        this.menu_trigger.on("click", function(){
            self.toggle();
        })
        this.host.find("[data-dismiss=menu]").each(function(i,e){
            e=$(e);
            e.on("click", function(){
                self.hide();
            })
        })
        $("body").append(this.overlay)
        $("body").append(this.host)
    }

    show() {
        console.log("Menu.show()")
        this.host.show();
        this.overlay.show();
    }

    hide() {
        console.log("Menu.hide()")
        this.host.hide();
        this.overlay.hide();
    }

    is_visible() {
        return this.host.is(":visible");
    }

    toggle() {
        return this.is_visible()?this.hide():this.show();
    }
}

var Menu = new MenuWidget();
