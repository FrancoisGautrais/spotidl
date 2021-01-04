

$(document).ready(function(){

    //$("h1").after(Template.instanciate("globalChart"))
    refresh();
})

function modal_alert(title, content=""){
    $("#alert-title").html(title)
    $("#alert-content").html(content)
    $("#alert-modal").modal("show")
}
