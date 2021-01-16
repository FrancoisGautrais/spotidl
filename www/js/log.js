

class LogTab {
    constructor(){
        this.opt={
            type: "track",
            page: 0,
            offset: 0,
            limit: 0
        }
        this.select_limit=$("#log_n_select")
        this.select_mode=$("#log_mode_select")
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
        this.opt.type=this.select_mode.val()
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

    showResults(res){
        this.data=res
        set_visible(this.next_btn, this.data.total>this.opt.offset+this.opt.limit)
        set_visible(this.prev_btn, this.opt.offset-this.opt.limit>=0)
        this.root.empty()
        console.log(res);
        for(var i in res.data){
            var d = res.data[i];
            var tmp={
                timestamp: Utils.timestampToStr(d.timestamp),
                url: d.data.url,
                refer: (d.type=="refer")?"Meta":"Piste",
                _data: d
            };
            if(d.type=="refer"){
                if(d.data.type=="track"){
                    tmp.type="Piste";
                    tmp.name=d.data.data.artists?d.data.data.artists[0].name:"?"
                    tmp.name+=d.data.data.album?("/"+d.data.data.album):"/?"
                    tmp.name+="/"+d.data.data.name;
                }
                if(d.data.type=="album"){
                    tmp.type="Album";
                    tmp.name=d.data.data.artist?d.data.data.artist:"?"
                    tmp.name+="/"+d.data.data.album;
                }
                if(d.data.type=="artist"){
                    tmp.type="Artiste";
                    tmp.name=d.data.data.name;
                }
            }else{
                tmp.type="Piste";
                tmp.name=d.data.artists?d.data.artists[0].name:"?"
                tmp.name+=d.data.album?("/"+d.data.album):"/?"
                tmp.name+="/"+d.data.name;
            }
            this.root.append(Template.instanciate("template-log-entry", tmp))
        }

    }

}

var Log = new LogTab()