String.prototype.formatUnicorn = String.prototype.formatUnicorn ||
function () {
    "use strict";
    var str = this.toString();
    if (arguments.length) {
        var t = typeof arguments[0];
        var key;
        var args = ("string" === t || "number" === t) ?
            Array.prototype.slice.call(arguments)
            : arguments[0];

        for (key in args) {
            str = str.replace(new RegExp("\\{" + key + "\\}", "gi"), args[key]);
        }
    }

    return str;
};

class Utils
{
    static CHARACTERS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPRQSTUVWXYZ0123456789";

    static  getRandomInt(max) {
      return Math.floor(Math.random() * Math.floor(max));
    }

    static randomId(n=16){
        var out=""
        var m = Utils.CHARACTERS.length;
        for(var i=0; i<n; i++) out+=Utils.CHARACTERS[Utils.getRandomInt(m)];
        return out+Date.now();
    }

    static formatDurationHMS(n){
        var out = "";
        n=Math.ceil(n)
        if(n>=3600){
            var h = Math.floor(n/3600)
            out+=h+"h "
            n=n%3600;
        }
        if(n>=60){
            var m = Math.floor(n/60)
            out+=m+"min "
            n=n%60;
        }
        if(n>0){
            out+=n+"s"
        }
        return out;
    }
}

class Template {

    static instanciate(templateid, data={}){
        var templateText = $("#"+templateid)[0].innerHTML
        templateText=templateText.formatUnicorn(data)
        var root =$(templateText)

        root.find("[id]").each(function(i,e){
            e=$(e)
            var oid = e.prop("id")
            var nid = "["+oid+"]"+Utils.randomId()
            e.prop("id", nid)
            root.find("[for="+oid+"]").prop("for", nid)
        })

        //find ne regarde pas dans l'lélement racine il faut passer par un parent pour l'utiliser
        var fakeroot=$("<div></div>");
        fakeroot.append(root)
        fakeroot.find("[data-template]").each(function(i,e){
            var elem =$(e)
            var attr=elem.attr("data-var")
            var ndata = attr=="."?data:(data?data[attr]:null);
            if(ndata){
                if(Array.isArray(ndata)){
                    var src = elem;
                    console.log(src.parent())
                    for(var j in ndata){
                        var nndata = ndata[j];
                        var dst = Template.instanciate(src.attr("data-template"), nndata)
                        dst.insertBefore(src)
                    }
                    src.remove()
                }else{
                    Template.replace(elem, ndata)
                }
            }else{
                Template.replace(elem, data)
            }
        })
        return fakeroot.children()
    }

    static replace(src, data={}){
        var dst = Template.instanciate(src.attr("data-template"), data)
        dst.insertAfter(src)
        src.remove()
    }
}