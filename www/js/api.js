
class DlAPI
{
    constructor(){
        this.url_base="/api/command"
    }

    url(x){
        var sep = ""
        if(x[0]!='/') sep = "/"
        return  this.url_base+sep+x
    }

    _ajax(url, ajax={}, headers={}, success=null, errorFct=null, errorText=null, customUrl=false){
        if(customUrl) return this.__ajax(url, ajax, headers, success, errorFct, errorText)
        return this.__ajax(this.url(url), ajax, headers, success, errorFct, errorText)
    }

    __ajax(url, ajax={}, headers={}, success=null, errorFct=null, errorText=null){
        var async=(success || errorFct || errorText)?true:false

        if(errorFct){
            var oldfct=errorFct;
            errorFct=function(_a, _b, _c) {
                if(!(!_a && _b=="error" && _c==""))
                {
                    var resp=null
                    try{
                        resp = JSON.parse(_a.responseText);
                        oldfct(resp, true, _c)
                    }catch(err){
                        resp=_a.responseText
                        oldfct(resp, false, _c)
                    }

                }else{
                    oldfct(null, _b, _c)
                }
            }
        }
        else{
            errorFct=function(_a, _b, _c) {
                if(!(!_a && _b=="error" && _c==""))
                {
                    var resp=""
                    try{
                        resp = JSON.parse(_a.responseText);
                        modal_alert("Erreur", (errorText?errorText:"Erreur")+ "( "+resp.code+" : '"+resp.message+"') : " + JSON.stringify(resp.data))
                    }catch(err){
                        resp=_a.responseText
                        toast_error(errorText?errorText:("Le serveur a répondu : '"+resp+"'"))
                    }

                }else{
                    toast_error( "Erreur : Le serveur a clos la connexion")

                }
                Loading.close()
            }
        }
        if(success){
            var oldsuccess=success;
            success= function(x) { return oldsuccess(x.data) }
        }

        var param = Object.assign({}, {
            type: 'get',
            url: url,
            async: async,
            dataType : "json",
            headers: headers,
            success :  success,
            error : errorFct
        }, ajax)
        //console.log("Request : ",param)

        var out = $.ajax(param)
        if(!async){
            return JSON.parse(out.responseText)
        }
        return out
    }

    ajax_get(url, opt={}){
        opt=Object.assign({
            headers : {}, ajax: {}, success : null, errorFct : null, errorText :null}, opt)
        return this._ajax(url, opt.ajax, opt.headers, opt.success, opt.errorFct, opt.errorText)
    }

    _ajax_get(url, opt={}){
        opt=Object.assign({
            headers : {}, ajax: {}, success : null, errorFct : null, errorText :null}, opt)
        console.log("URL ='"+url+"'")
        return this._ajax(url, opt.ajax, opt.headers, opt.success, opt.errorFct, opt.errorText, true)
    }

    ajax_delete(url, opt={}){
        opt=Object.assign({headers : {}, ajax: {}, success : null, errorFct : null, errorText :null}, opt)
        return this._ajax(url, Object.assign({type: 'delete'}, opt.ajax), opt.headers, opt.success, opt.errorFct, opt.errorText)
    }

    ajax_post(url, data=null, opt={}){
        opt=Object.assign({ ajax : {}, headers : {}, success : null, errorFct : null, errorText :null}, opt)
        return this._ajax(url, Object.assign({type: 'post', data: JSON.stringify(data)}, opt.ajax),
                Object.assign({"Content-Type": "application/json"}, opt.headers), opt.success, opt.errorFct, opt.errorText)
    }

    ajax_put(url, data=null, opt={}){
        opt=Object.assign({ ajax : {}, headers : {}, success : null, errorFct : null, errorText :null}, opt)
        return this._ajax(url, Object.assign({type: 'put', data: JSON.stringify(data)}, opt.ajax),
                Object.assign({"Content-Type": "application/json"}, opt.headers), opt.success, opt.errorFct, opt.errorText)
    }

    count(opt={}){
        return this.ajax_get("count", opt)
    }
    running(opt={}){
        return this.ajax_get("running", opt)
    }
    done(opt={}){
        return this.ajax_get("done", opt)
    }

    queue(opt={}){
        return this.ajax_get("queue", opt)
    }

    running(opt={}){
        return this.ajax_get("queue/running", opt)
    }

    add_url(url, opt={}){
        return this.ajax_get("add/"+url, opt)
    }

    list(url, opt={}){
        return this.ajax_get("list/"+url, opt)
    }

    cancel_running(url, opt={}){
        return this.ajax_get("running/cancel/"+url, opt)
    }

    restart_running(url, opt={}){
        return this.ajax_get("running/restart/"+url, opt)
    }

    remove_queue(url, opt={}){
        return this.ajax_get("queue/remove/"+url, opt)
    }

    clear_queue(opt={}){
        return this.ajax_get("clear/queue", opt)
    }

    clear_all(opt={}){
        return this.ajax_get("clear/all", opt)
    }

    clear_errors(opt={}){
        return this.ajax_get("clear/errors", opt)
    }

    remove_errors(i, opt={}){
        return this.ajax_get("remove/errors/"+i, opt)
    }

    remove_done(i, opt={}){
        return this.ajax_get("remove/done/"+i, opt)
    }


    clear_done(opt={}){
        return this.ajax_get("clear/done", opt)
    }

    add_post(data, opt={}){
        return this.ajax_post("add", data, opt)
    }

    list_file(url, opt={}){
        return this.ajax_post("list", data, opt)
    }

    set_config(data, opt={})
    {
        return this.ajax_post("config", data, opt)
    }

    get_config(data, opt={})
    {
        return this.ajax_get("config",opt)
    }

    subsonic_start_scan(opt={})
    {
        return this.ajax_get("subsonic/scan/start", opt)
    }

    subsonic_status_scan(opt={})
    {
        return this.ajax_get("subsonic/scan/status", opt)
    }

    subsonic_test(data, opt={})
    {
        return this.ajax_post("subsonic/test", data, opt)
    }

    restart_error(index, opt={})
    {
        return this.ajax_get("restart/error/"+index,opt)
    }

    manual_error(index, url, opt={})
    {
        return this.ajax_post("restart/error/"+index, {url: url},opt)
    }

    ping(url, opt={})
    {
        opt=Object.assign({
            ajax: {
                timeout: 1000
            }
        }, opt)
        this._ajax_get(url, opt)
    }
    exit(opt={})
    {

        if(dump) return this.ajax_get("exit/true",opt)
        return this.ajax_get(url,opt)
    }
    restart(opt={})
    {
        return this.ajax_get("restart",opt)
    }

    static SEARCH_ALBUM="album"
    static SEARCH_ALBUM="track"
    static SEARCH_ARTIST="artist"
    search(text, type, opt={}){
        return this.ajax_get("search/"+text+"?type="+type, opt)
    }
}

var API = new DlAPI()