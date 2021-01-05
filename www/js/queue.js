


$(document).ready(function(){
    refresh(null, true)
})

function td(x){
    return $("<td>"+x+"</td>")
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
}