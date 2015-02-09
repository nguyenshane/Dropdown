# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def login():
    return dict()

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def create_account(first_name, last_name, email, password):
    user = None
    if(not db(db.auth_user.email == email).select().first()):
        user = db.auth_user.insert( 
                first_name = first_name, 
                last_name = last_name, 
                password = password, 
                email  = email,
                )
    return user


def check_access():
    return True if auth.is_logged_in() else False
    

@request.restful()
def api():
    response.view = 'generic.json' #+request.extension
    def GET(*args,**vars):
        if args[0] == 'create_account':
            logger.info(vars)
            epas = vars['epas']
            epasdecode = epas.decode('base64').split(':')
            email = epasdecode[0]
            password = CRYPT()(epasdecode[1])[0]
            firstname = vars['firstname']
            lastname = vars['lastname']
            user = create_account(firstname, lastname, email, password)

            if (user != None):
                success=True
            else: 
                success=False
            return dict(success=success)

        if args[0] == 'signin':
            auth.basic()
            logger.info(request.env.http_authorization)
            logger.info(auth.user)
            success=check_access()
            return dict(success=success)

        if args[0] == 'logout':
            logger.info('Logging out')
            #logger.info(request.env.http_authorization)
            #auth.basic()

            #logger.info(auth.user)
            if auth.user:
                auth.logout()
            
            success=check_access()
            return dict(success=success)

        else:
            patterns = 'auto'
            parser = db.parse_as_rest(patterns,args,vars)


            if parser.status == 200:
                return dict(content=parser.response)
            else:
                raise HTTP(parser.status,parser.error)
    
    auth.settings.allow_basic_login = True
    @auth.requires_login()
    def POST(table_name,**vars):
        return db[table_name].validate_and_insert(**vars)
    def PUT(table_name,record_id,**vars):
        return db(db[table_name]._id==record_id).update(**vars)
    def DELETE(table_name,record_id):
        return db(db[table_name]._id==record_id).delete()
    def OPTIONS(*args,**vars):
        print "OPTION called"
        return True
    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE, OPTIONS=OPTIONS)


# @auth.requires_login() 
# def api():
#     """
#     this is example of API with access control
#     WEB2PY provides Hypermedia API (Collection+JSON) Experimental
#     """
#     from gluon.contrib.hypermedia import Collection
#     rules = {
#         '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
#         }
#     return Collection(db).process(request,response,rules)
