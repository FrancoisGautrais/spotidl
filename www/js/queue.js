var QUEUE_REFRESH=2000
var QUEUE_DATA=null;

$(document).ready(function(){
    refresh(null, true)
})

function td(x){
    return $("<td>"+x+"</td>")
}
/*
function refresh(data=null, cont=false)
{
    if(data==null){
        API.queue({
            success: function(data){
                refresh(data.queue, cont);
            }
        })
        return;
    }
    $("#queue-root").empty()
    for(var i in data){
        var track=data[i]
        var tr = $("<tr></tr>")
        tr.append(td(i+""))
        tr.append(td(track.name))
        tr.append(td(track.album))
        tr.append(td(track.artists[0].name))
        $("#queue-root").append(tr)
    }
    if(cont){
        setTimeout(function(){
            refresh(null, true)
        },3000)
    }
}*/

function process_input_running(r){
    return Object.assign(r,{
        id: r.id,
        track_time: Utils.formatDurationHMS(r.track_time),
        track: process_input_track(r.track),
        progress : (r.progress!=null)?r.progress:"",
        url: (r.track)?r.track.url:r.id,
        class: (r.track)?"":"hidden"
    })
}

function process_input_track(track){
    if(track){
        return Object.assign(track,{
            duration: Utils.formatDurationHMS(track.duration),
            artist: (track.artists)?track.artists[0].name:"none"
        })
    }else{
        return {
            url: "none",
            name : "none",
            duration : "-",
            artist : "none",
            artists : [],
            album : "none",
            track_number : "-",
            class: "hidden"
        }
    }
}

function process_input_error(err){
    return Object.assign(err,{
        track: process_input_track(err.track)
    })
}

CURRENT_RUNNING=[]
function process_queue_input(data){
    for(var i in data){
        data[i]=process_input_running(data[i])
    }
    return data
}

function process_queue_input(data){
    for(var i in data.errors){
        data.errors[i]=process_input_error(data.errors[i])
    }
    for(var i in data.running){
        data.running[i]=process_input_running(data.running[i])
    }
    CURRENT_RUNNING=data.running
    for(var i in data.done){
        data.done[i]=process_input_track(data.done[i])
    }
    for(var i in data.queue){
        data.queue[i]=process_input_track(data.queue[i])
    }
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
    console.log("data:", data)
    var tpl = Template.instanciate("template-queue-root", data);
    restore_queue_table_visibility(tpl)
    $("#queue-root").empty()
    $("#queue-root").append(tpl)
    if(cont){
        setTimeout(function(){
            refresh(null, true)
        },QUEUE_REFRESH)
    }
}

function is_running_file_change(data)
{
    if(CURRENT_RUNNING.length!=data.length) return true;
    for(var i=0; i<data.length; i++){
        if(data[i].url!=CURRENT_RUNNING[i].url)
            return true
    }
    return false
}

function update_running(data=null, cont=false)
{
    if(data==null){
        API.running({
            success: function(data){
                refresh(data, cont);
            }
        })
        return;
    }
    QUEUE_DATA=Object.assign({}, data)

    data=process_running_input(data)
    var changed = is_running_file_change(data)
    CURRENT_RUNNING=data
    if(changed){
        refresh()
    }else{


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

