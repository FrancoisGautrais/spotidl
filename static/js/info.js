

class SelectionTab {
    static MODE_ARTISTS="artists"
    static MODE_PLAYLIST="playlist"
    constructor(){
        var self=this;
        this.dict_reulsts={}
        this.results=[]
        this.refer=[]
        this.root=$("#info-list")
        this.set_mode(SelectionTab.MODE_ARTISTS, false)
        this.mode_is_changing=false
        //this.current_mode="artists"
    }

    select_all(type, id){
        if(type) this.root.find("input[data-type=track-checkbox][data-"+type+"id='"+id+"']").prop("checked", true)
        else this.root.find(".track-checkbox").prop("checked", true)
        this.on_selection_changed()
    }

    unselect_all(type, id){
        if(type) this.root.find("input[data-type=track-checkbox][data-"+type+"id='"+id+"']").prop("checked", false)
        else this.root.find(".track-checkbox").prop("checked", false)
        this.on_selection_changed()
    }

    get_selected(){
        var out={
            tracks: [],
            refer: this.refer
        }
        var self = this
        this.root.find("input[data-type=track-checkbox]:checked").each(function(i,e){
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
        var btn = this.root.find(".toggle-artist, .toggle-album").each(function(i, e){
            e=$(e);
            if(e.find("i").html()!="expand_more")
                e.click()
        })
    }

    fold_all(){
        var btn = this.root.find(".toggle-artist, .toggle-album").each(function(i, e){
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
        if(type=="artist") elem=this.root.find("tbody[data-artistid='"+id+"'][data-type='artist-content']")
        if(type=="album") elem=this.root.find("table[data-albumid='"+id+"'][data-type='album-content']")
        elem.toggle()
        var child = $('<i class="material-icons">'+(elem.is(":visible")?'expand_more':'chevron_right')+'</i>')
        elem=null;
        var parent=null;
        if(type=="artist") elem=this.root.find("a.toggle-artist[data-artistid='"+id+"']")
        if(type=="album") elem=this.root.find("a.toggle-album[data-albumid='"+id+"']")
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
        this.on_selection_changed();
        this.clear_filter_bar();
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
                album["artist"]=artiste.name;
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
        this._show_results(data);
    }

    show(){
        $("#info-tab-trigger").click()
    }

    hide(){
        $("#info-tab-trigger").hide()
    }

    clear_filter_bar(){
        $("#selection-filter-input").val("")
        this.on_filter_input_change("")
    }

    count_visible_tracks(e){
        var obj = {n:0}
        e.find("[data-type=track]").each(function(i,e){
            if($(e).data("visible")=="true") obj.n++;
        })
        return obj.n
    }

    count_checked_tracks(e){
        var obj = {n:0}
        e.find("[data-type='track-checkbox']").each(function(i,e){
            if($(e).is(":checked")) obj.n++;
        })
        return obj.n
    }

    count_total_tracks(e){
        return e.find("[data-type=track]").length;
    }

    on_filter_input_change(val){
        var self=this;
        var ptr = { n:0}
        var patterns=val.toLowerCase().split(" ")
        this.root.find("[data-type=track]").each(function(i,e){
            e=$(e);
            var search=e.data("search").toLowerCase();
            var found=true;
            for(var j in patterns){
                if(patterns[j]!="" && !search.includes(patterns[j])){
                    e.data("visible", "false")
                    set_visible(e, false);
                    return;
                }
            }
            e.data("visible", "true")
            set_visible(e, true);
        })

        if(this.current_mode==SelectionTab.MODE_ARTISTS){
            this.root.find("[data-type=album]").each(function(i,e){
                e=$(e);
                var n = self.count_visible_tracks(e)
                set_visible(e, n>0);
            })
            this.root.find("[data-type=artist]").each(function(i,e){
                e=$(e);
                var n = self.count_visible_tracks(e)
                set_visible(e, n>0);
            })
        }
    }

    set_icon_checkbox_value(icon, n, total){
        if(n==0){
            icon.html("check_box_outline_blank")
            icon.data("state", "false")
        }else if(n==total){
            icon.html("check_box")
            icon.data("state", "true")
        }else{
            icon.html("indeterminate_check_box")
            icon.data("state", "")
        }
    }

    on_selection_changed(){
        var self=this;
        if(this.current_mode==SelectionTab.MODE_ARTISTS){
            this.root.find("[data-type=album]").each(function(i,e){
                e=$(e);
                var albumid = e.data("albumid")
                var n = self.count_checked_tracks(e)
                var total = self.count_total_tracks(e)
                var icon = e.find("#i-album-"+albumid)
                e.find("#nb-selected-album-"+albumid).html(n)
                e.find("#nb-total-album-"+albumid).html(total)
                self.set_icon_checkbox_value(icon, n, total)
            })
            this.root.find("[data-type=artist]").each(function(i,e){
                e=$(e);
                var artistid = e.data("artistid")
                var n = self.count_checked_tracks(e)
                var total = self.count_total_tracks(e)
                var icon = e.find("#i-artist-"+artistid)
                e.find("#nb-selected-artist-"+artistid).html(n)
                e.find("#nb-total-artist-"+artistid).html(total)
                self.set_icon_checkbox_value(icon, n, total)
            })
        }
        var n = this.count_checked_tracks(this.root)
        var total =  this.count_total_tracks(this.root)
        $("#nb-selected").html(n)
        $("#nb-total").html(total)
        self.set_icon_checkbox_value($("#i-null-total"), n, total)
    }

    on_toggle_select(type, elem, id){
        var state = elem.data("state")+"";
        if(state=="true"){
            this.unselect_all(type, id)
        } else {
            this.select_all(type, id)
        }
    }

}

var Selection = new SelectionTab()