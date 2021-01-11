

class SelectionTab {
    static MODE_ARTISTS="artists"
    static MODE_PLAYLIST="playlist"
    constructor(){
        this.dict_reulsts={}
        this.results=[]
        this.refer=[]
        this.set_mode(SelectionTab.MODE_PLAYLIST, false)
        this.mode_is_changing=false
        //this.current_mode="artists"
    }

    select_all(type, id){
        if(type) $("input[data-type=track-checkbox][data-"+type+"id='"+id+"']").prop("checked", true)
        else $(".track-checkbox").prop("checked", true)
    }

    unselect_all(type, id){
        if(type) $("input[data-type=track-checkbox][data-"+type+"id='"+id+"']").prop("checked", false)
        else $(".track-checkbox").prop("checked", false)
    }



    get_selected(){
        var out={
            tracks: [],
            refer: this.refer
        }
        var self = this
        $("input[data-type=track-checkbox]:checked").each(function(i,e){
            var url = $(e).data("url");
            out.tracks.push(self.dict_reulsts[url])
        })
        return out
    }

    has_data(){
        return this.results.length>0
    }

    download(){
        var data = this.get_selected();
        var self = this
        Loading.open();
        API.add_post(data,{
            success: function(d){
                toast(d.count+" fichiers ajoutés")
                Loading.close()
                $("#info-list").hide()
                $("#no-info-list").show()
                self.dict_reulsts={}
                self.results=[]
                self.refer=[]
            }
        });
        $("#template-root").empty()
    }

    cancel(){
        $("#template-root").empty()
        $("#info-list").hide()
        $("#no-info-list").show()
    }

    unfold_all(){
        var btn = $(".toggle-artist, .toggle-album").each(function(i, e){
            e=$(e);
            if(e.find("i").html()!="expand_more")
                e.click()
        })
    }

    fold_all(){
        var btn = $(".toggle-artist, .toggle-album").each(function(i, e){
            e=$(e);
            if(e.find("i").html()=="expand_more")
                e.click()
        })
    }

    set_mode(m, update=true){
        this.mode_is_changing=true
        $("#info_mode_select").val(m)
        this.current_mode=m
        this.mode_is_changing=false
        if(update && this.has_data())this.show_results(this.results)
    }


    toggle_table(type, id){
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

    _show_results(data){
        var tpl = null;
        if(this.current_mode==SelectionTab.MODE_ARTISTS)
        {
            tpl=Template.instanciate("template-allartists", data);
        }else if(this.current_mode==SelectionTab.MODE_PLAYLIST){
            tpl=Template.instanciate("template-playlist", Object.values(this.dict_reulsts));
        }
        $("#template-root").empty()
        $("#template-root").append(tpl)
        this.fold_all();
        this.show();
        $("#info-list").show()
        $("#no-info-list").hide()
    }

    show_results(data){
        if(this.mode_is_changing) return
        if(Array.isArray(data)){
            data={ artists: data, count: data.length, refer: this.refer}
        }
        var out = data.count+" fichiers titre à la liste d'attente<br>"
        this.refer=data.refer
        this.results=data=data.artists;
        this.dict_reulsts={}
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
                    track["track"]=albumid;
                    track["albumid"]=albumid;
                    track["artist"]=artiste.name;
                    track["artistid"]=artistid;
                    track["duration"]=Utils.formatDurationHMS(track["duration"])
                    this.dict_reulsts[track.url]=Object.assign({}, track)
                }
            }
        }
        this._show_results(data)
    }

    show(){
        $("#info-tab-trigger").click()
    }

    hide(){
        $("#info-tab-trigger").hide()
    }

}

var Selection = new SelectionTab()