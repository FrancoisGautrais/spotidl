

class SearchTab
{
    constructor(){

    }


    show_results(data)
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

    search(ele) {
        var text = $(ele).val()
        var prefix = text.substring(0,text.length>8?8:text.length)
        if(prefix.length<3){
            this.hide_search_results();
            return;
        }
        if("https://".startsWith(prefix) && (event.key === 'Enter'))
        {
            this.hide_search_results();
            this.on_send()
        }else{
            this.show_search_results();
            var self=this;
            API.search(text, "artist,album,track", {
                success: function(d){ self.show_results(d)},
                errorFct: function(x,y,z){
                    modal_alert("Erreur", "Erreur inconnue")
                }
            })
        }
    }

    show_search_results(){
        $("#search_results").show()
    }

    hide_search_results(){
        $("#search_results").hide()
    }


    handle_download_all(data) {
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

    handle_info(data)
    {
        var self=this;
        if(data.count>20){
            Loading.close()
            modal_download(data.count, function(){ //download all
                self.handle_download_all(data);
            },
            function(){ //select
                Selection.show_results(data)
            });
            $("#search-bar").val("")
            Queue.refresh();
        }else{
            self.handle_download_all(data);
            $("#search-bar").val("")
            Queue.refresh();
        }
    }

    on_send(val=null)
    {
        var self=this;
        if(!val) val = $("#search-bar").val()
        if(val.startsWith("https://open.spotify.com/")){
            Loading.open()
            API.list(val, {
                success: function(d){self.handle_info(d)},
                errorFct: function(x,y,z){
                    modal_alert("Erreur", "Erreur inconnue")
                }
            })
        }
        else{
            modal_alert("Erreur", "Url '"+val+"' invalide")
        }
    }


    on_upload(){
       var self = this;
       var fd = new FormData();
       fd.append("file", $("#file-value")[0].files[0])
       jQuery.ajax({
            url: "/api/command/list",
            type: "post",
            data: fd,
            processData: false,
            contentType: false,
            success: function (result, r2, r3) {
                 self.handle_info(result.data)
            }
        });
    }
}

var Search = new SearchTab();