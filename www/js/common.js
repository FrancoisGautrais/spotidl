
function modal_alert(title, content=""){
    $("#alert-title").html(title)
    $("#alert-content").html(content)
    $("#alert-modal").modal("show")
}

var MODAL_CALLBACK={
}

function modal_call(name, args=[]){
    var fct = MODAL_CALLBACK[name];
    if(fct){
        fct.apply(args);
    }
}

function set_modal_callback(name, fct=null){
    MODAL_CALLBACK[name]=fct
}

function modal_download(n, download_all, download_select){
    set_modal_callback('download_all', download_all)
    set_modal_callback('download_select', download_select)
    $("#download-n-tracks").html(n+"")
    $("#download-modal").modal("show")
}