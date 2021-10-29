
var Login=null;

class LoginPage
{
    constructor(){
        var self = this;
        this.db = new DataBind("login-card")
        $("#login-card").find("[data-bind]").on('keypress',function(e){
            if(e.which == 13) {
                self.connect()
            }
        })
    }

    connect(){
        var data = this.db.updateFields()
        var self = this;
        API.ajax_post("user/auth", data,{
            success: function(d){self.on_success(d)},
            errorFct:  function(a,b,c){self.on_error(a,b,c)}
        } )
    }

    on_error(a,b,c){
        if(b)
            toast_error(a.data)
        else
            toast_error(a)
        this.db.field("username", "")
        this.db.field("password", "")
    }

    on_success(data){
        window.location.href="/"
    }

    static init(){
        Template.ready(function(){
            Login=new LoginPage();
        })
    }
}

LoginPage.init()
