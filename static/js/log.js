

class LogTab {
    constructor(){
        this.opt={
            type: "refer",
            page: 0,
            offset: 0,
            limit: 0
        }
        this.select_limit=$("#log_n_select")
        this.next_btn=$("#log-results-next")
        this.prev_btn=$("#log-results-prev")
        this.root=$("#log-content")
        set_visible(this.next_btn, false)
        set_visible(this.prev_btn, false)
        this.data={}
    }

    send()
    {
        this.opt.page=0;
        this.opt.offset=0;
        this.opt.limit=parseInt(this.select_limit.val())
        this._send();
    }

    set_mode(elem){
        elem=$(elem)
        this.send();
    }

    _send(){
        var self = this;
        API.get_logs(this.opt, {
            success: function(d){
                self.showResults(d);
            }
        })
    }

    next(){
        if(this.data.total>this.opt.offset+this.opt.limit){
            this.opt.page++;
            this.opt.offset+=this.opt.limit;
            this._send();
        }
    }

    prev(){
        if(this.opt.offset-this.opt.limit>=0){
            this.opt.page--;
            this.opt.offset-=this.opt.limit;
            this._send();
        }
    }

    processTrack(track){
        var out=process_input_track(track, track.data.data);
        return out;
    }


    process_results(d){
        console.log(d)
        var data = d;
        var ts = Utils.timestampToStr(d.timestamp)
        var artiste = data;
        var artistid = Utils.randomId();
        artiste["artistid"]=artistid;
        artiste.timestamp=ts;
        artiste.album_count=0;
        artiste.track_count=0;
        artiste.ok_count=0;
        artiste.fail_count=0;
        for(var j in artiste.albums){
            var album = artiste.albums[j];
            var albumid = Utils.randomId();
            album["albumid"]=albumid;
            album["artistid"]=artistid;
            album["artist"]=artiste.name;
            album.timestamp=ts;
            artiste.album_count++;
            album.track_count=0
            album.ok_count=0
            album.fail_count=0
            for (var k in album.tracks){
                var track = album.tracks[k];
                track["track"]=albumid;
                track["albumid"]=albumid;
                track["artist"]=artiste.name;
                track["artistid"]=artistid;
                track["duration"]=Utils.formatDurationHMS(track["duration"])
                track.timestamp=Utils.timestampToStr(track.timestamp);
                artiste.track_count++;
                album.track_count++;
                if(track.state=="ok"){
                    album.ok_count++;
                    artiste.ok_count++;
                }else if(track.state=="error"){
                    album.fail_count++;
                    artiste.fail_count++;
                }
            }
            if(album.ok_count==album.track_count){
                album.state="ok"
            }else if(album.fail_count>0){
                album.state=(album.fail_count==album.track_count)?"error":"mixed"
            }else{
                album.state="running"
            }
        }
        if(artiste.ok_count==artiste.track_count){
            artiste.state="ok"
        }else if(artiste.fail_count>0){
            artiste.state=(artiste.fail_count==artiste.track_count)?"error":"mixed"
        }else{
            artiste.state="running"
        }
    }

    showResults(res){
        this.data=res
        set_visible(this.next_btn, this.data.total>this.opt.offset+this.opt.limit)
        set_visible(this.prev_btn, this.opt.offset-this.opt.limit>=0)
        this.root.empty()
        for(var i in res.data){
            var d = res.data[i];
            this.process_results(d);
            this.root.append(Template.instanciate("template-log-entry-artist", d))
        }
        this.fold_all()
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
}

var Log = new LogTab()