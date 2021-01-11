var QUEUE_REFRESH=1000
var QUEUE_DATA=null;

$(document).ready(function(){
    refresh(null, true)
})

function td(x){
    return $("<td>"+x+"</td>")
}



var YOUTUBE_MANUAL=null

var DB_YOUTUBE=null
var YOUTUBE_ERROR_INDEX=0
$(document).ready(function(){
    DB_YOUTUBE=new DataBind("input-youtube");
})

function process_input_running(r){
    return Object.assign(r,{
        id: r.id,
        track_time: Utils.formatDurationHMS(r.track_time),
        track: process_input_track(r.track),
        progress : (r.progress!=null)?itof(r.progress,1):"0",
        url: (r.track)?r.track.url:r.id,
        class: (r.track)?"":"hidden"
    })
}

function process_input_error(err){
    return Object.assign(err,{
        track: process_input_track(err.track)
    })
}

CURRENT_RUNNING=[]
function process_queue_running(data){
    for(var i in data){
        data[i]=process_input_running(data[i])
    }
    return data
}

function process_queue_input(data){
    var len = data.errors.length
    var tmp = []
    for(var i in data.errors){
        if(!data.errors[i]) continue
        var x = process_input_error(data.errors[i])
        x.index=i;
        tmp.push(x)
    }
    data.errors=tmp


    for(var i in data.running){
        if(!data.running[i]) continue
        data.running[i]=process_input_running(data.running[i])
    }
    CURRENT_RUNNING=data

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

function restore_queue_table_visibility(temp){
    var elem;
    var arr = [ "errors", "running", "done", "queue" ]

    for(var i in arr){
        var type = arr[i];
        var tab = $("[data-id='queue-"+type+"']");
        if(tab && !tab.is(":visible"))
            queue_table_visibility(type, false, temp)
    }
}

function refresh(data=null, cont=false)
{
    if(data==null){
        API.queue({
            success: function(data){
                refresh(data, cont);
            }
        })
        return;
    }
    QUEUE_DATA=Object.assign({}, data)

    data=process_queue_input(data)
    var tpl = Template.instanciate("template-queue-root", data);
    restore_queue_table_visibility(tpl)
    $("#queue-root").empty()
    $("#queue-root").append(tpl)
    if(cont){
        setTimeout(function(){
            update_running(null, true)
        },QUEUE_REFRESH)
    }
}

function is_running_file_change(data)
{
    if(!CURRENT_RUNNING || CURRENT_RUNNING.running.length!=data.running.length) return true;
    for(var i=0; i<data.running.length; i++){
        if(data.running[i].url!=CURRENT_RUNNING.running[i].url)
            return true
    }
    return data.running_count!=CURRENT_RUNNING.running_count ||
        data.queue_count!=CURRENT_RUNNING.queue_count ||
        data.errors_count!=CURRENT_RUNNING.errors_count ||
        data.done_count!=CURRENT_RUNNING.done_count
}

function update_running(data=null, cont=false)
{
    if(data==null){
        API.running({
            success: function(data){
                update_running(data, cont);
            }
        })
        return;
    }
    data=Object.assign({}, data)

    data.running=process_queue_running(data.running)
    var changed = is_running_file_change(data)
    CURRENT_RUNNING=data
    if(changed){
        refresh(null, true)
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
                update_running(null, true)
            },QUEUE_REFRESH)
        }
    }
}

function queue_elem_remove(url)
{
    API.remove_queue(url, {
        success: function(){refresh();}
    })
}

function queue_clear_queue()
{
    var n=QUEUE_DATA?QUEUE_DATA.queue_count:null;
    if(n<=0) return;
    confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer toutes la file d'attente ("+
                    n+" fichiers) ?",
            function(){
            API.clear_queue({
                success: function(){refresh();}
            })
        }
    )
}

function queue_clear_running()
{
    API.clear_running({
        success: function(){refresh();}
    })
}

function queue_clear_done()
{
    API.clear_done({
        success: function(){refresh();}
    })
}

function queue_errors_remove(index) {
    var n=QUEUE_DATA?QUEUE_DATA.errors_count:null;
    if(n<=0) return;
    API.remove_errors(index, {
        success: function(){refresh();}
    })
}

function queue_errors_restart(index)
{
    var track = QUEUE_DATA.errors[index]
    API.restart_error(YOUTUBE_ERROR_INDEX,{
        success: function(d){
            toast("1 fichier ajouté")
        }
    })
}

function queue_errors_manual(index)
{
    YOUTUBE_MANUAL = QUEUE_DATA.errors[index]
    YOUTUBE_ERROR_INDEX=index
    DB_YOUTUBE.field("url", "")
    $("#input-youtube").modal()
}

function queue_errors_manual_valid()
{
    DB_YOUTUBE.updateFields()
    var  url = DB_YOUTUBE.fields.url
    console.log("url====",url)
    API.manual_error(YOUTUBE_ERROR_INDEX, url, {
        success: function(d){
            toast("1 fichier ajouté")
        }
    })
}

function queue_clear_errors()
{
    var n=QUEUE_DATA?QUEUE_DATA.errors_count:null;
    if(n<=0) return;
    confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer toutes les erreurse ("+
                    n+" éléments) ?",
            function(){
            API.clear_errors({
                success: function(){refresh();}
            })
        }
    )
}

function queue_clear_all()
{
    confirm("Êtes vous sur ?", "Voulez vous vraiment supprimer la file d'attente"+
                " toutes les erreurs et la liste des éléments téléchargés ?",
            function(){
            API.clear_all({
                success: function(){refresh();}
            })
        }
    )
}

function toggle_queue(type)
{
    var table =$("[data-id='queue-"+type+"']")
    if(table.is(":visible")){
        queue_table_visibility(type, false)
    }else{
        queue_table_visibility(type, true)
    }
}


function remove_done(id){
    API.remove_done(id, {
        success: function(){refresh();}
    })
}

function remove_queue(id){
    API.remove_done(id, {
        success: function(){refresh();}
    })
}

function cancel_job(url) {
    API.cancel_running(url, {
        success: function(){refresh();}
    })
}

function restart_job(url) {
    API.restart_running(url, {
        success: function(){refresh();}
    })
}

function queue_table_visibility(type, val, temp=null){
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

function open_youtube_search(){
    var url = "https://www.youtube.com/results?search_query="
    var terms=YOUTUBE_MANUAL.track.name+" "+YOUTUBE_MANUAL.track.artist
    url+=terms.replaceAll(" ", "+")
    openInNewTab(url)
}