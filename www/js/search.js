
function show_short_results(data)
{
    var artistsdiv = $("#search-results-col-artist")
    var trackdiv = $("#search-results-col-track")
    var albumdiv = $("#search-results-col-album")
    artistsdiv.empty()
    trackdiv.empty()
    albumdiv.empty()
    if(data.artists) data.artists=process_input_artists_array(data.artists.items)
    if(data.tracks) data.tracks=process_input_tracks_array(data.tracks.items, true)
    if(data.albums) data.albums=process_input_albums_array(data.albums.items)

    artistsdiv.append(Template.instanciate("template-artists-short-table", data))
    trackdiv.append(Template.instanciate("template-tracks-short-table", data))
    albumdiv.append(Template.instanciate("template-albums-short-table", data))

}

function search(ele) {
    var text = $(ele).val()
    var prefix = text.substring(0,text.length>8?8:text.length)
    if(prefix.length<3){
        hide_short_search_results();
        return;
    }
    if("https://".startsWith(prefix) && (event.key === 'Enter'))
    {
        hide_short_search_results();
        on_send()
    }else{
        show_short_search_results();
        API.search(text, "artist,album,track", {
            success: show_short_results,
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur inconnue")
            }
        })
    }
}

function show_short_search_results(){
    $("#search_results").show()
}

function hide_short_search_results(){
    $("#search_results").hide()
}


function handle_download_all(data) {
    var out={
        tracks: [],
        refer: data.refer

    }

    for(var i in data.artists){ //artists
        var artiste = data.artists[i];
        for(var j in artiste.albums){
            var album = artiste.albums[j];
            for (var k in album.tracks){
                out.tracks.push(album.tracks[k]);
            }
        }
    }
    API.add_post(out,{
        success: function(d){
            toast(d.count+" fichiers ajoutés !")
            Loading.close()
        }
    });
}

function handle_info(data)
{
    if(data.count>20){
        Loading.close()
        modal_download(data.count, function(){ //download all
            handle_download_all(data);
        },
        function(){ //select
            Selection.show_results(data)
        });
        $("#search-bar").val("")
        refresh();
    }else{
        handle_download_all(data);
        $("#search-bar").val("")
        refresh();
    }
}

function on_send(val=null)
{
    if(!val) val = $("#search-bar").val()
    if(val.startsWith("https://open.spotify.com/track/")){
        Loading.open()
        API.add_url(val, {
            success: function(d){
                toast(d.count+" fichiers ajoutés !")
                Loading.close()

            },
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur inconnue")
            }
        })
    }
    else if(val.startsWith("https://open.spotify.com/")){
        Loading.open()
        API.list(val, {
            success: handle_info,
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur inconnue")
            }
        })
    }
    else{
        modal_alert("Erreur", "Url '"+val+"' invalide")
    }
}


function on_upload(){

   var fd = new FormData();
   fd.append("file", $("#file-value")[0].files[0])
   jQuery.ajax({
        url: "/api/command/list",
        type: "post",
        data: fd,
        processData: false,
        contentType: false,
        success: function (result, r2, r3) {
             handle_info(result.data)
        }
    });
}
