
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

    _ajax(url, ajax={}, headers={}, success=null, errorFct=null, errorText=null){
        var async=(success || errorFct || errorText)?true:false
        if(errorFct){
            var oldfct=errorFct
            errorFct=function(_a, _b, _c) {
                if(!(!_a && _b=="error" && _c==""))
                {
                    var resp = JSON.parse(_a.responseText);
                    console.log(resp)
                    error( (errorText?errorText:"Erreur")+ "( "+resp.code+" : '"+resp.message+"') : " + resp.data)
                }else{
                    error( "Erreur : Le serveur a clos la connexion")
                }
                Loading.close()
                oldfct(resp, _b, _c)
            }
        }
        if(errorFct==null){
            errorFct=function(_a, _b, _c) {
                if(!(!_a && _b=="error" && _c==""))
                {
                    var resp = JSON.parse(_a.responseText);
                    error( (errorText?errorText:"Erreur")+ "( "+resp.code+" : '"+resp.message+"') : " + JSON.stringify(resp.data))
                }else{
                    error( "Erreur : Le serveur a clos la connexion")

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
            url: this.url(url),
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

    add_url(url, opt={}){
        return this.ajax_get("add/"+url, opt)
    }
}

var API = new DlAPI()