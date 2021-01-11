

class _Parameters
{
    constructor(){
        this.db = new DataBind("parameters-div");
        this.config={}
        this.load();
    }

    save(){
        Loading.open();
        API.set_config(this.db.fields,{
            success:function(d){
                self.db.set_fields(d)
                Loading.close()
                toast("Configuration envoyé ! Redémarrez le serveur pour appliquer les modifications")
            }
        })
    }

    get_new_url(port){
        return  window.location.protocol+"//"+window.location.hostname+":"+port+window.location.pathname+"api/command/ping"
    }

    ping(port){
        var self = this;
        console.log("-------Ping "+port)
        API.ping(this.get_new_url(port),{
            success: function(d){

                console.log("Ping ok ")
                Loading.close()
                window.location.href=window.location.protocol+"//"+window.location.hostname+":"+
                            port+window.location.pathname;
            },
            errorFct: function(d){

                setTimeout(function(){
                    console.log("ping fail "+port)
                    self.ping(port)
                }, 1000)
            }
        })
    }

    save_and_restart(){
        Loading.open();
        var self=this;
        API.set_config(this.db.fields,{
            success:function(d){
                self.db.set_fields(d)
                console.log("saved")
                API.restart({
                    success:function(){
                        toast("Redémarrage du serveur")
                        setTimeout(function(){
                            self.ping(self.db.fields.server.port)
                        }, 500)

                }})
            }
        })
    }


    load(){
        Loading.open();
        var self = this
        API.get_config(this.config,{
            success:function(d){
                self.db.set_fields(d)
                Loading.close()
            }
        })
    }

    get(x){
        var obj = this.db.updateFields()
        if(x) return obj[x]
        return obj
    }


    server_exit(b){
        API.exit(b, function(d){
        })
    }

    server_restart(){
        API.restart(function(d){
        })
    }

}

var Config = null;

Template.on_loaded(function(){
    Config=new _Parameters();
})
