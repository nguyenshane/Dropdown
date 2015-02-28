# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import random
#from faceb import FaceBookAccount

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
def showfriendFacebook():
    
    friendlist = FaceBookAccount().get_friend()
    
def test_show_user():
    user_id = request.args(0)
    return show_user(user_id)
    
def show_user(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    #linktable_ref = db(db.linktable.user_id == auth.user_id).select()
    test_create_table = db(db.test_create_table.user_id == user_id).select()
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
    #auth.settings.login_form = FaceBookAccount()
    return dict(form = auth.login())

@auth.requires_login()
def test_add_friend():
    friend_id = request.args(0)
    friend = db(db.auth_user.id == friend_id).select().first()
    isAdded = add_friend(auth.user_id,friend_id)
    return dict(friend=friend,isAdded=isAdded)

def add_friend(from_user_id,to_user_id):
    if isFriend(from_user_id,to_user_id):
        return False
    db.friend_table.insert(from_user_id=from_user_id,to_user_id=to_user_id,created_on=datetime.utcnow())
    return True

def isFriend(from_user_id,to_user_id):
    fromIdObj = db(db.auth_user.id == from_user_id).select().first()
    toIdObj = db(db.auth_user.id == to_user_id).select().first()
    exist_data = db((db.friend_table.from_user_id==fromIdObj) & (db.friend_table.to_user_id == toIdObj)).select().first()
    

    if exist_data is not None:
        return True
    else:
        return False
    

@auth.requires_login()
def test_show_all_friend():
    friendlist = show_all_friend(auth.user_id)
    #grid = SQLTABLE(friendlist)
    return dict(friendlist=friendlist)

def show_all_friend(user_id):
    friendlist = db(db.friend_table.from_user_id == user_id).select(orderby=~db.friend_table.created_on)
    
    return friendlist


@auth.requires_login()
def test_show_all_user():
    userlist = show_all_user()
    
    def generate_addfriend_button(row):
        b = 'Added'
        if not isFriend(auth.user_id,row.id):
            b = A('Add Friend', _class='btn', _href=URL('default', 'test_add_friend', args=[row.id]))
        return b
    
    links = [
        dict(header='', body = generate_addfriend_button),
        ]
    grid = SQLFORM.grid(db.auth_user,
                        fields=[db.auth_user.first_name,db.auth_user.last_name,db.auth_user.email,db.auth_user.point],
                        details=False,csv=False,links=links,editable=False, deletable=False)
    return dict(grid = grid)

def show_all_user():
    userlist = db().select(db.auth_user.ALL, orderby=db.auth_user.id)
    
    return userlist

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
    #auth.settings.login_form=FaceBookAccount()
    return dict(form=auth())
    #return dict(login_form = auth())


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
            auth.basic()
            #auth.settings.login_form=FaceBookAccount()
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
