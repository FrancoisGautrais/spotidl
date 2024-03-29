
class DlAPI
{
    constructor(){
        this.url_base=""
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
            //console.log("URL ='"+url+"'")
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
        return this.ajax_get("queue/count", opt)
    }
    running(opt={}){
        return this.ajax_get("queue/running", opt)
    }
    done(opt={}){
        return this.ajax_get("queue/done", opt)
    }

    queue(opt={}){
        return this.ajax_get("queue", opt)
    }

    add_url(url, opt={}){
        return this.ajax_get("queue/add/"+url, opt)
    }

    list(url, opt={}){
        return this.ajax_get("queue/list?url="+url, opt)
    }

    cancel_running(url, opt={}){
        return this.ajax_get("queue/running/cancel?url="+url, opt)
    }

    restart_running(url, opt={}){
        return this.ajax_get("queue/running/restart?url="+url, opt)
    }

    remove_queue(url, opt={}){
        return this.ajax_get("queue/remove/"+url, opt)
    }

    clear_queue(opt={}){
        return this.ajax_get("queue/clear", opt)
    }

    clear_all(opt={}){
        return this.ajax_get("queue/clear/clear", opt)
    }

    clear_errors(opt={}){
        return this.ajax_get("queue/errors/clear", opt)
    }

    remove_errors(i, opt={}){
        return this.ajax_get("queue/errors/"+i+"/remove", opt)
    }

    remove_done(i, opt={}){
        return this.ajax_get("queue/done/remove"+i, opt)
    }

    restart_error(index, opt={})
    {
        return this.ajax_get("queue/error/"+index+"/restart",opt)
    }



    clear_done(opt={}){
        return this.ajax_get("queue/done/clear", opt)
    }

    add_post(data, opt={}){
        return this.ajax_post("queue/add", data, opt)
    }

    list_file(url, opt={}){
        return this.ajax_post("queue/list", data, opt)
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
    manual_error(index, url, opt={})
    {
        return this.ajax_post("queue/error/"+index+"/restart", {url: url},opt)
    }

    get_logs(data, opt={})
    {

        return this.ajax_get("logs?"+Utils.dictToParams(data),opt)
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

    search(text, data, opt={}){
        data=Object.assign({type: "artist,track,album", offset: 0, limit: 10}, data)
        return this.ajax_get("search/"+text+"?type="+data.type+"&offset="+data.offset+"&limit="+data.limit, opt)
    }
}

var API = new DlAPI()