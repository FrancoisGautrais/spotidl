

function search(ele) {
    if(event.key === 'Enter') {
        on_send()
    }
}

function handle_download_all(data) {
    var out=[]
    for(var i in data){ //artists
        var artiste = data[i];
        for(var j in artiste.albums){
            var album = artiste.albums[j];
            for (var k in album.tracks){
                out.push(album.tracks[k]);
            }
        }
    }
    API.add_post(out);
}

function handle_info(data)
{
    if(data.count>20){
        modal_download(data.count, function(){ //download all
            handle_download_all(data.artists);
        },
        function(){ //select
            show_results(data)
        });
        $("#search-bar").val("")
        refresh();
    }else{
        handle_download_all(data.artists);
        $("#search-bar").val("")
        refresh();
    }
}

function on_send()
{
    var val = $("#search-bar").val()
    if(val.startsWith("https://open.spotify.com/track/")){
        API.add_url(val, {
            success: handle_info,
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur inconnue")
            }
        })
    }
    else if(val.startsWith("https://open.spotify.com/")){
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
