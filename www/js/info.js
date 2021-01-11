var RESULTS={}
var TMP=null
function show_results(data){
    var out = data.count+" fichiers titre à la liste d'attente<br>"
    data=data.artists;
    RESULTS={}
    for(var i in data){ //artists
        var artiste = data[i];
        var artistid = Utils.randomId();
        artiste["artistid"]=artistid;
        for(var j in artiste.albums){
            var album = artiste.albums[j];
            var albumid = Utils.randomId();
            album["albumid"]=albumid;
            album["artistid"]=artistid;
            for (var k in album.tracks){
                var track = album.tracks[k];
                RESULTS[track.url]=Object.assign({}, track)
                track["track"]=albumid;
                track["albumid"]=albumid;
                track["artistid"]=artistid;
                track["duration"]=Utils.formatDurationHMS(track["duration"])
            }
        }
    }
    TMP=data
    var tpl = Template.instanciate("template-allartists", data);
    $("#template-root").empty()
    $("#template-root").append(tpl)
    info_fold_all();
    show_info_tab();
    $("#info-list").show()
    $("#no-info-list").hide()
}


function show_info_tab(){
    $("#info-tab-trigger").click()
}

function hide_info_tab(){
    $("#info-tab-trigger").hide()
}

function toggle_table(type, id){
    var elem=null;
    if(type=="artist") elem=$("tbody[data-artistid='"+id+"'][data-type='artist-content']")
    if(type=="album") elem=$("table[data-albumid='"+id+"'][data-type='album-content']")
    elem.toggle()
    var child = $('<i class="material-icons">'+(elem.is(":visible")?'expand_more':'chevron_right')+'</i>')
    elem=null;
    var parent=null;
    if(type=="artist") elem=$("a.toggle-artist[data-artistid='"+id+"']")
    if(type=="album") elem=$("a.toggle-album[data-albumid='"+id+"']")
    elem.empty()
    elem.append(child)
}

function select_all(type, id, val) {
    $("input[data-type=track-checkbox][data-"+type+"id='"+id+"']").prop("checked", val)
}

function get_selected_tracks(){
    var out=[]
    $("input[data-type=track-checkbox]:checked").each(function(i,e){
        var url = $(e).data("url");
        out.push(RESULTS[url])
    })
    return out
}

function download_selected(){
    var data = get_selected_tracks();
    Loading.open();
    API.add_post(data,{
        success: function(d){
            toast(d.count+" fichiers ajoutés")
            Loading.close()
            $("#info-list").hide()
            $("#no-info-list").show()
        }
    });
    $("#template-root").empty()
}

function cancel_selected(){
    $("#template-root").empty()
    $("#info-list").hide()
    $("#no-info-list").show()
}

function info_unfold_all(){
    var btn = $(".toggle-artist, .toggle-album").each(function(i, e){
        e=$(e);
        if(e.find("i").html()!="expand_more")
            e.click()
    })
}

function info_fold_all(){
    var btn = $(".toggle-artist, .toggle-album").each(function(i, e){
        e=$(e);
        if(e.find("i").html()=="expand_more")
            e.click()
    })
}

function info_select_all(){
    $(".track-checkbox").prop("checked", true)
}

function info_unselect_all(){
    $(".track-checkbox").prop("checked", false)
}