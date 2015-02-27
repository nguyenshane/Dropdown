# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import random
#from faceb import FaceBookAccount


## Define oauth application id and secret.





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
    #exercise = db().select(db.exercise.ALL, orderby=db.exercise.name)
    #exercise = db.exercise
    #exercise = db((db.exercise.id ==3) & (db.exercise.id==2)).select()

    if db(db.circuit).isempty():
        return dict(grid=None)
    lastCircuit = db().select(db.circuit.ALL).last()
    maxNum = lastCircuit.id;
    
    num1 = random.randint(1, maxNum)
    num2 = random.randint(1, maxNum)
    num3 = random.randint(1, maxNum)
    while(num2 == num1 or num2 == num3):
         num2 = random.randint(1, maxNum)
    while(num3 == num1 or num3 == num2):
         num3 = random.randint(1, maxNum)
        
    exercise = (db.circuit.id ==num1 ) | (db.circuit.id ==num2) | (db.circuit.id ==num3)

    #exercise = db().select(db.exercise.ALL, orderby='<random>', limitby=(0,2))

    #exercise = db.executesql('SELECT * FROM exercise ORDER BY RAND() LIMIT 1')

    logger.info(exercise)


    def generate_complete_button(row):
        b = A('Complete', _class='btn', _href=URL('default', 'complete', args=[row.id]))
        return b
    
    links = [
        dict(header='', body = generate_complete_button),
        ]
    

    grid = SQLFORM.grid(exercise,csv=False,links=links,editable=False, deletable=False)
    return dict(grid=grid)

    #return locals()

@auth.requires_login()
def showfriend():
    #facebook_app_id = '1056851497687275'
    #user = facebook.get_user_from_cookie(request.cookies,'1056851497687275', "40ae04477987bed07074b8886d82b8bc")
    #profile = None
    friendlist = FaceBookAccount().get_friend()
    #if user:
    #    graph = facebook.GraphAPI(user["access_token"])
    #    profile = graph.get_object("me")
    #    friends = graph.get_connections("me", "friends")
    
    return dict(friendlist=friendlist)
    
@auth.requires_login()
def showuser():
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    #linktable_ref = db(db.linktable.user_id == auth.user_id).select()
    test_create_table = db(db.test_create_table.user_id == auth.user_id).select()
    return dict(userrev=userrev,test_create_table=test_create_table)


def show():
    exercise = db.exercise(request.args(0,cast=int)) or redirect(URL('index'))
    point = exercise.point
    
    return dict(exercise=exercise,point=point)

@auth.requires_login()
def complete():
    
    content = None
    
    circuit_id = request.args(0)
    
    cir = db(db.circuit.id == circuit_id).select().first()
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    
    point = cir.point
    newpoint = int(cir.point)
    form2 = FORM.confirm('Did you complete this exercise')
    if form2.accepted:
        redirect(URL('default', 'showuser'))
    newpoint += point
    userrev.update_record(point=newpoint)
    
    #linktable_id = db.linktable.insert(user_id = auth.user_id,exercise_id = exerciseid,exercise_name=exer.name)
    db.test_create_table.insert(user_id = auth.user_id,circuit_id = cir.id,circuit_count=1,created_on=datetime.utcnow())
    
    content = form2
        
    
    return dict(content=content,cir=cir,userrev=userrev)

@auth.requires_login()
def reset():
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    userrev.point = 0
    userrev.update_record()
    db(db.linktable.user_id == auth.user_id).delete()
    
    form = FORM.confirm('You will reset your point')
    if form.accepted:
        redirect(URL('default', 'index'))
    
    return dict(form=form)

@auth.requires_login()
def upgrade():
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    myadmin = db(db.auth_group.role == "myadmin").select().first()
    db.auth_membership.insert(user_id = userrev.id,group_id = myadmin.id)
    
    
    return dict()

@auth.requires_membership('myadmin')
def add_exercise():
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    
    form = SQLFORM.factory(Field('name',label='Exercise Name'),Field('point','integer'),Field('body','text',label='Discription'))
    form.add_button('Cancel', URL('default', 'index'))
    
    if form.process().accepted:
        db.exercise.insert(name=form.vars.name,point=form.vars.point,body=form.vars.body)
        # Successful processing.
        session.flash = T("new exercise created")
        redirect(URL('default', 'index'))
    return dict(form=form)

def login_with_facebook():
    auth.settings.login_form = FaceBookAccount()
    return dict(form = auth.login())


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
    auth.settings.login_form=FaceBookAccount()
    #return dict(form=auth())
    return dict(login_form = auth())


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
    
def new_circuit(user):

    return obj


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
            #auth.basic()
            auth.settings.login_form=FaceBookAccount()
            #logger.info(request.env.http_authorization)
            #logger.info(auth.user)
            success=check_access()
            today_circuit = get_today_circuit(auth.user.id)

            return dict(success=success,today_circuit=today_circuit)

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

def get_today_circuit(user_id):

    query_daily = db(db.daily.user_id==user_id).select()
    today_circuit = []
    exercise_sets = []
    exercises = []

    for e in query_daily:
        
        _circuit = db(db.circuit.id==e.circuit_id).select()
        
        _exercise_sets = db(db.exercise_set.set_name==_circuit[0].exercise_set_name).select()

        for each_set in _exercise_sets:
            exercises += db(db.exercise.id==each_set.exercise_id).select()

        today_circuit += _circuit
        exercise_sets += _exercise_sets

    logger.info(today_circuit)
        
    return dict(today_circuit=today_circuit,exercise_sets=exercise_sets,exercises=exercises)



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
