class QueueTab
{
    static QUEUE_REFRESH=1000
    static TASK_ID="Queue Init";

    constructor()
    {
        this.youtube_index=0
        this.db_youtube=new DataBind("input-youtube");
        this.youtube_manual=null
        this.current_running=[]
        this.queue_data=null
        this.refresh(null, true)
    }


    process_running(r){
        return Object.assign(r,{
            id: r.id,
            track_time: Utils.formatDurationHMS(r.track_time),
            track: process_input_track(r.track),
            progress : (r.progress!=null)?itof(r.progress,1):"0",
            url: (r.track)?r.track.url:r.id,
            class: (r.track)?"":"hidden"
        })
    }

    process_error(err){
        return Object.assign(err,{
            track: process_input_track(err.track)
        })
    }

    process_running_list(data){
        for(var i in data){
            data[i]=this.process_running(data[i])
        }
        return data
    }

    process_input(data){
        var len = data.errors.length
        var tmp = []
        for(var i in data.errors){
            if(!data.errors[i]) continue
            var x = this.process_error(data.errors[i])
            x.index=i;
            tmp.push(x)
        }
        data.errors=tmp


        for(var i in data.running){
            if(!data.running[i]) continue
            data.running[i]=this.process_running(data.running[i])
        }
        this.current_running=data

        len = data.done.length
        tmp=[]
        for(var i in data.done){
            if(!data.done[len-1-i]) continue
            tmp.push(process_input_track(data.done[len-1-i]))
        }
        data.done=tmp

        len = data.queue.length
        tmp=[]
        for(var i in data.queue){
            if(!data.queue[i]) continue
            tmp.push(process_input_track(data.queue[i]))
        }
        data.queue=tmp
        return data
    }

    restore_table_visibility(temp){
        var elem;
        var arr = [ "errors", "running", "done", "queue" ]

        for(var i in arr){
            var type = arr[i];
            var tab = $("[data-id='queue-"+type+"']");
            if(tab && !tab.is(":visible"))
                this.table_visibility(type, false, temp)
        }
    }

    refresh(data=null, cont=false)
    {
        var self=this;
        if(data==null){
            API.queue({
                success: function(data){
                    self.refresh(data, cont);
                }
            })
            return;
        }
        this.queue_data=Object.assign({}, data)

        data=this.process_input(data)
        var tpl = Template.instanciate("template-queue-root", data);
        this.restore_table_visibility(tpl)
        $("#queue-root").empty()
        $("#queue-root").append(tpl)
        if(cont){
            setTimeout(function(){
                self.update_running(null, true)
            },QueueTab.QUEUE_REFRESH)
        }
        App.finished(QueueTab.TASK_ID)
    }

    is_running_file_change(data)
    {
        if(!this.current_running || this.current_running.running.length!=data.running.length) return true;
        for(var i=0; i<data.running.length; i++){
            if(data.running[i].url!=this.current_running.running[i].url)
                return true
        }
        return data.running_count!=this.current_running.running_count ||
            data.queue_count!=this.current_running.queue_count ||
            data.errors_count!=this.current_running.errors_count ||
            data.done_count!=this.current_running.done_count
    }

    update_running(data=null, cont=false)
    {
        var self=this;
        if(data==null){
            API.running({
                success: function(data){
                    self.update_running(data, cont);
                }
            })
            return;
        }
        data=Object.assign({}, data)

        data.running=this.process_running_list(data.running)
        var changed = this.is_running_file_change(data)
        this.current_running=data
        if(changed){
            this.refresh(null, true)
        }else{
            for(var i in data.running){
                var r = data.running[i]
                $("#queue-running-state-"+r.id).html(r.state)
                $("#queue-running-time-"+r.id).html(r.track_time)
                $("#queue-running-progress-"+r.id).attr("aria-valuenow", r.progress)
                $("#queue-running-progress-"+r.id).css("width", r.progress+"%")
                $("#queue-running-progress-"+r.id).html(r.progress+"%")
            }

            if(cont){
                setTimeout(function(){
                    self.update_running(null, true)
                },QueueTab.QUEUE_REFRESH)
            }
        }
    }

    remove_element(url)
    {
        var self = this;
        API.remove_queue(url, {
            success: function(){self.refresh();}
        })
    }

    clear_queue()
    {
        var self = this;
        var n=this.queue_data?this.queue_data.queue_count:null;
        if(n<=0) return;
        confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer toutes la file d'attente ("+
                        n+" fichiers) ?",
                function(){
                API.clear_queue({
                    success: function(){self.refresh();}
                })
            }
        )
    }

    clear_running()
    {
        var self = this;
        API.clear_running({
            success: function(){self.refresh();}
        })
    }

    clear_done()
    {
        var self = this;
        API.clear_done({
            success: function(){self.refresh();}
        })
    }

    errors_remove(index) {
        var self = this;
        var n=this.queue_data?this.queue_data.errors_count:null;
        if(n<=0) return;
        API.remove_errors(index, {
            success: function(){self.refresh();}
        })
    }

    errors_restart(index)
    {
        var track = this.queue_data.errors[index]
        API.restart_error(this.youtube_index,{
            success: function(d){
                toast("1 fichier ajouté")
            }
        })
    }

    errors_manual(index)
    {
        this.youtube_manual = this.queue_data.errors[index]
        this.youtube_index=index
        this.db_youtube.field("url", "")
        $("#input-youtube").modal()
    }

    errors_manual_valid()
    {
        this.db_youtube.updateFields()
        var  url = this.db_youtube.fields.url
        console.log("url====",url)
        API.manual_error(this.youtube_index, url, {
            success: function(d){
                toast("1 fichier ajouté")
            }
        })
    }

    clear_errors()
    {
        var self = this;
        var n=QueueTab.this.queue_data?QueueTab.this.queue_data.errors_count:null;
        if(n<=0) return;
        confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer toutes les erreurse ("+
                        n+" éléments) ?",
                function(){
                API.clear_errors({
                    success: function(){self.refresh();}
                })
            }
        )
    }

    queue_clear_all()
    {
        var self=this;
        confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer la file d'attente"+
                    " toutes les erreurs et la liste des éléments téléchargés ?",
                function(){
                API.clear_all({
                    success: function(){self.refresh();}
                })
            }
        )
    }

    toggle(type)
    {
        var table =$("[data-id='queue-"+type+"']")
        if(table.is(":visible")){
            this.table_visibility(type, false)
        }else{
            this.table_visibility(type, true)
        }
    }


    remove_queue(id){
        var self=this;
        API.remove_done(id, {
            success: function(){self.refresh();}
        })
    }

    cancel_job(url) {
        var self=this;
        API.cancel_running(url, {
            success: function(){self.refresh();}
        })
    }

    restart_job(url) {
        var self=this;
        API.restart_running(url, {
            success: function(){self.refresh();}
        })
    }

    table_visibility(type, val, temp=null){
        var a_str = "[data-id='a-"+type+"']";
        var table_str = "[data-id='queue-"+type+"']";

        var a = temp?temp.find(a_str):$(a_str)
        var table = temp?temp.find(table_str):$(table_str)
        if(val){
            table.show()
        }else{
            table.hide()
        }
        a.html($('<i class="material-icons">'+(val?'expand_more':'chevron_right')+'</i>'))
    }

    open_youtube_search(){
        var url = "https://www.youtube.com/results?search_query="
        var terms=this.youtube_manual.track.name+" "+this.youtube_manual.track.artist
        url+=terms.replaceAll(" ", "+")
        openInNewTab(url)
    }
}
var Queue = null;


App.enqueue_to_load(function(){
    Queue = new QueueTab(QueueTab.TASK_ID)
}, QueueTab.TASK_ID)