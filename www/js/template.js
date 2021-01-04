

class Template {

    static instanciate(templateid){
        var root =$($("#"+templateid)[0].innerHTML)

        root.find("[id]").each(function(i,e){
            e=$(e)
            var nid = Utils.randomId()
            var oid = e.prop("id")
            e.prop("id", nid)
            root.find("[for="+oid+"]").prop("for", nid)
        })

        root.find("template[src]").each(function(i,e){
            Template.replace($(e))
        })
        return root
    }

    static replace(src){
        var dst = Template.instanciate(src.attr("src"))
        dst.insertAfter(src)
        src.remove()
    }
}