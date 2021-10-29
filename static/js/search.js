

class SimpleSearchTab
{
    constructor(){
        this.root=$("#simple-search")
        this.enable=true;
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
        if(ele) ele=$(ele)
        var text = ele.val()
        var prefix = text.substring(0,text.length>8?8:text.length)
        if(prefix.length<1){
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
            API.search(text, {type: "artist,album,track"}, {
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
            url: "/queue/list",
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

var Search = new SimpleSearchTab();

class AdvancedSearchTab
{
    static DEFAULT_LIMIT=10
    constructor(){
        this.root=$("#advanced-search")
        this.results_div=$("#advanced_search_results")
        this.btn_prev=$("#advanced-results-prev")
        this.btn_next=$("#advanced-results-next")
        this.enable=false;
        this.opt = {
            limit: AdvancedSearchTab.DEFAULT_LIMIT,
            offset: 0,
            query: "",
            type: "artist"
        }
        this.page=0
    }

    search(ele){
        if(ele) ele=$(ele)
        var text = ele.val()
        var prefix = text.substring(0,text.length>8?8:text.length)
        this.opt.query=text
        this.opt.type = this.find_selected_type()
        if(prefix.length<1){
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
            this.opt.offset=0
            this.opt.page=0
            API.search(this.opt.query, this.opt, {
                success: function(d){ self.show_results(d)},
                errorFct: function(x,y,z){
                    modal_alert("Erreur", "Erreur inconnue")
                }
            })
        }
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
            $("#advanced-search-bar").val("")
            Queue.refresh();
        }else{
            self.handle_download_all(data);
            $("#advanced-search-bar").val("")
            Queue.refresh();
        }
    }


    find_selected_type(){
        return $("[name=as-type]:checked").attr("value")
    }

    hide_search_results(){
        $(".advanced_search_results_root").hide();
        this.opt.offset=0
        this.opt.page=0
        this.opt.query=""
    }

    show_search_results(){
        $(".advanced_search_results_root").show();
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

    show_results(data)
    {
        this.results_div.empty()
        if(data.artists && this.opt.type=="artist"){
            set_visible($("#advanced-results-next"), data.artists.next!=null)
            set_visible($("#advanced-results-prev"), data.artists.previous!=null)
            data.artists=process_input_artists_array(data.artists.items)
            this.results_div.append(Template.instanciate("template-artists-short-table", data))
        }

        if(data.tracks && this.opt.type=="track") {
            set_visible($("#advanced-results-next"), data.tracks.next!=null)
            set_visible($("#advanced-results-prev"), data.tracks.previous!=null)
            data.tracks=process_input_tracks_array(data.tracks.items, true)
            this.results_div.append(Template.instanciate("template-tracks-short-table", data))
        }

        if(data.albums && this.opt.type=="album") {
            set_visible($("#advanced-results-next"), data.albums.next!=null)
            set_visible($("#advanced-results-prev"), data.albums.previous!=null)
            data.albums=process_input_albums_array(data.albums.items)
            this.results_div.append(Template.instanciate("template-albums-short-table", data))
        }


    }


    __nav(){
        var self=this;
        API.search(this.opt.query, this.opt, {
            success: function(d){ self.show_results(d)},
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur inconnue")
            }
        })
    }

    next() {
        this.opt.offset+=this.opt.limit;
        this.__nav();
    }

    prev() {
        this.opt.offset-=this.opt.limit;
        this.__nav();
    }



}

var AdvancedSearch = new AdvancedSearchTab();


function show_simple_search(){
    Search.root.show()
    Search.enable=true;
    AdvancedSearch.root.hide()
    AdvancedSearch.enable=false;
}

function show_advanced_search(){
    Search.root.hide()
    Search.enable=false;
    AdvancedSearch.root.show()
    AdvancedSearch.enable=true;
}

function search_on_send(url){
    if(Search.enable){
        Search.on_send(url);
    }else{
        AdvancedSearch.on_send(url);
    }
}


App.ready(function(){
    show_simple_search();
})
