

$(document).ready(function(){

    //$("h1").after(Template.instanciate("globalChart"))
    refresh(null, true)
})

function modal_alert(title, content=""){
    $("#alert-title").html(title)
    $("#alert-content").html(content)
    $("#alert-modal").modal("show")
}

function search(ele) {
    if(event.key === 'Enter') {
        on_send()
    }
}

function td(x){
    return $("<td>"+x+"</td>")
}

function on_send()
{
    var val = $("#search-bar").val()
    if(val.startsWith("https://open.spotify.com/")){
        API.add_url(val, {
            success: function(data){
                modal_alert("Succès", data+" pistes ajoutées")
                $("#search-bar").val("")
                refresh();
            },
            errorFct: function(x,y,z){
                modal_alert("Erreur", "Erreur incoonue")

            }
        })
    }
    else{
        modal_alert("Erreur", "Url '"+val+"' invalide")
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


