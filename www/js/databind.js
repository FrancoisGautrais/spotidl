function set_visible(x, val){
    if(val) x.show()
    else x.hide()
}
class DataBind {
    /*
        data-bind="NAME[:TYPE]" -> this.NAME (TYPE: default str)
        data-on="METOD:EVENT" -> this.METHOD(elem)
    */
    static __events=[null, "change", "keyup", "keydown", "click", "paste"]
    constructor(domid){
        this.__id=domid
        this.fields={}
        this.__cb_object={}
        this.__cb_callbacks={}
        this.__if_cb={}
        this._root=$("#"+this.__id)
        this._updateBind()
        this._set_if_cb()
    }

    _refresh_if_cb(){
        for(var name in this.__if_cb[name]){
            var arr = this.__if_cb[name];
            for(var i in arr){
                arr[i]();
            }
        }
    }

    __set_if_cb(self, trigger, inv){
        var fct = function(){
            var val = trigger.is(":checked");
            set_visible(self, val);
        }
        fct();
        var name = trigger.data("bind").split(":")[0]
        if(this.__if_cb[name]==undefined){
            this.__if_cb[name]=[]
        }
        this.__if_cb[name].push(fct)
        trigger.on("change", fct)
    }
    _set_if_cb(){
        var self=this;
        var root = this._root;
        $("[data-if]").each(function(i,e){
            e=$(e)
            var element =  e.data("if")
            if(element.length==0) return;
            var inv =false;
            if(element && element.length>1 && element[0]=="!"){
                inv=true;
                element=element.substring(1,element.length-1)
            }
            self.__set_if_cb($(e), $("[data-bind^='"+element+"']"), inv)
        })

    }

    __get_callback(e){
        if(!("length" in e)) e=$(e)
        var elem = e[0]
        for(const id in this.__cb_object){
            if(elem==this.__cb_object[id]) return this.__cb_callbacks[id]
        }
        var id = Utils.randomId()
        this.__cb_callbacks[id] = {
        }
        this.__cb_object[id] = elem
        return this.__cb_callbacks[id]
    }
    on(e, event, src, fct){
        var self = this
        if(!("length" in e)) e=$(e)
        var self = this
        var cbo = this.__get_callback(e)
        if(!(event in cbo) ){
            self.__set_base_callback(e, event);
        }
        cbo[event][src]=fct
    }
    __set_base_callback(e, event){
        if(!("length" in e)) e=$(e)
        var self = this
        var cbo = this.__get_callback(e)
        if(!(event in cbo) ){
            cbo[event]={}
            e.on(event, function(){
                var cb = cbo[event];
                if("bind" in cb){
                    cb["bind"](e)
                }
                for(const key in cb){
                    if(key!="bind"){
                        cb[key](e)
                    }
                }
            })
        }
    }

    _updateBind(){
        var self = this
        for(const i in DataBind.__events){
            var evt = DataBind.__events[i]
            var suffix =(evt)?("-"+evt):""
            this._root.find("[data-bind"+suffix+"]").each(function(i,e){
                self._bindData($(e), evt, suffix)
            })
            this._root.find("[data-on"+suffix+"]").each(function(i,e){
                self._bindOn($(e), evt, suffix)
            })
        }
        this.updateFields()
    }

    __get_field(e){
        var tag = e.prop("tagName").toLowerCase()
        var bind = e.data("bind").split(":")
        var type = (bind.length>1)?bind[1]:"string"
        var value = null

        switch(tag){
            case "input":
                switch(e.attr("type")){
                    case "checkbox":
                        value=e.is(":checked")
                        type="bool"
                        break;
                    default:
                        if(e.hasClass("datepicker")){
                            type="date"
                        }
                        value=e.val()
                        break

                }break;
            case "select":
                value=e.val()
                break
            default:
                value=e.html()
        }
        switch(type){
            case "int":
                value=parseInt(value)
                break;
            case "float":
                value=parseInt(value)
                break;
            case "date":
                value=date_to_int(value)
                break;
            case "bool":
                value=((""+value).toLowerCase()!="false") && (value!="0")
                break;
        }

        //this.fields[bind[0]]=value
        this._set_data_by_path(bind[0], value)
    }


    __set_field(e, value){
        var tag = e.prop("tagName").toLowerCase()

        var bind = e.data("bind").split(":")
        var type = (bind.length>1)?bind[1]:"string"
        //this.fields[bind[0]]=value
        this._set_data_by_path(bind[0], value)

        switch(tag){
            case "textarea":
            case "input":
                switch(e.prop("type")){
                    case "checkbox":
                        e.prop("checked", value)
                        break;
                    default:
                        if(e.hasClass("datepicker")){
                            type="date"
                            value=e.val(int_to_date(value))
                        }
                        else {
                            value=e.val(value)
                        }
                        break

                }break;
            case "select":
                value=e.val(value)
                break
            default:
                value=e.html(value)
        }
        var arr = this.__if_cb[bind[0]]
        for(var i in arr){
            arr[i]()
        }
    }

    getElemByBind(f){
        for(const key in DataBind.__events){
            var evt = DataBind.__events[key]
            var suffix = (evt)?("-"+evt):""
            var tmp = this._root.find("[data-bind"+suffix+"="+f+"]")
            if(tmp.length) return tmp
        }
        return null
    }


    _bindData(e, event=null, suffix){
        var self = this
        event=this.__find_evt(e, event)

        if(!event) event="change"
        this.on(e, event, "bind", function(){
            self.__get_field(e)
        })
    }

    _bindOn(e, evt=null, suffix){
        var self = this
        var method = e.data("on"+suffix)
        evt=this.__find_evt(e, event)

        this.on(e, evt, "on" ,function(){
            var x = e.data("args")
            if(!x){
                self[method](e, evt)
            }else{
                x=eval(x)
                if(Array.isArray(x)){
                    self[method](...x)
                }else{
                    self[method](x)
                }
            }
        })
    }


    __find_evt(e, evt){
        var tag = e.prop("tagName").toLowerCase()
        if(evt) return evt
        switch(tag){
            case "a":
            case "button":
                evt = "click"
            break;
            case "input":
                switch(e.attr("type")){
                    case "text":
                    case "number":
                    case "email":
                    case "password":
                    case "search":
                    case "tel":
                    case "url":
                        evt = "keyup"
                        if(e.hasClass("datepicker")) evt="change";
                        break;
                    default:
                        evt = "change"
                }
                break;
            default:
                evt = "change"
        }
        return evt

    }

    _get_path_root(path){
        path = path.split(".")
        var acc = this.fields;
        for(var i=0; i<path.length-1; i++){
            var name = path[i];
            if(!(name in acc)){
                acc[name]={}
            }
            acc=acc[name]
        }
        return [acc, path[path.length-1]]
    }

    _set_data_by_path(path, value){
        var tmp = this._get_path_root(path)
        tmp[0][tmp[1]]=value;
    }

    _get_data_by_path(path){
        var tmp = this._get_path_root(path)
        return tmp[0][tmp[1]];
    }


    field(name, val){

        if(typeof name == "string"){
            var e = this._root.find("[data-bind='"+name+"']")
            if(!e.length){
                e= this._root.find("[data-bind^='"+name+":']")
            }

            if(e.length){
                if(val==undefined){
                    this.__get_field(e)
                }else{
                    this.__set_field(e, val)
                }
            }
        }else{
            for(const key in name){
                this.field(key, name[key])
            }
        }
    }

    _set_field_recurs(path, obj){
        path=(path=="")?path:(path+".")
        for(const key in obj){
            if($.isPlainObject(obj[key])){
                this._set_field_recurs(path+key, obj[key])
            }
            else
            {
                this.field(path+key, obj[key])
            }
        }
    }

    set_fields(obj){
        this._set_field_recurs("", obj)
    }

    updateFields(){
        var self = this
        this._root.find("[data-bind]").each(function(i,e){
            self.__get_field($(e))
        })
        return this.fields

    }

    cb(e, f){
        alert("--- "+e+" "+f)
    }
}
