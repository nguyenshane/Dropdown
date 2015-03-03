# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import random
import ast
import json
#from faceb import FaceBookAccount


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
        b = A('Complete', _class='btn', _href=URL('default', 'test_complete', args=[row.id]))
        return b
    
    links = [
        dict(header='', body = generate_complete_button),
        ]
    

    grid = SQLFORM.grid(exercise,csv=False,links=links,editable=False, deletable=False)
    return dict(grid=grid)

    #return locals()


    

#########################################################
##List of test backend function####
#########################################################

def test_show_user():
    user_id = request.args(0)
    return show_user(user_id)

def test_show_circuit():
    circuit_id = request.args(0)
    circuit = get_circuit(circuit_id)
    exercise_set = get_exercise_set(circuit.exercise_set_name)    
    return dict(circuit=circuit,exercise_set=exercise_set)

def test_show_exercise():
    exercise_id = request.args(0)
    exercise = get_exercise(exercise_id)    
    return dict(exercise=exercise)

@auth.requires_login()
def test_complete():    
    circuit_id = request.args(0)
    cir = db(db.circuit.id == circuit_id).select().first()
    complete_circuit(auth.user_id,circuit_id)    
    return dict(cir=cir)


@auth.requires_login()
def test_reset():
    reset_point(auth.user_id)    
    return dict()

@auth.requires_login()
def test_upgrade():
    isUpgrade = upgrade(auth.user_id)    
    return dict(isUpgrade=isUpgrade)

    
@auth.requires_login()
def showfriendFacebook():    
    friendlist = FaceBookAccount().get_friend()

@auth.requires_login()
def test_add_friend():
    friend_id = request.args(0)
    friend = db(db.auth_user.id == friend_id).select().first()
    isAdded = add_friend(auth.user_id,friend_id)
    return dict(friend=friend,isAdded=isAdded)


@auth.requires_login()
def test_show_all_friend():
    friendlist = show_all_friend(auth.user_id)
    #grid = SQLTABLE(friendlist)
    return dict(friendlist=friendlist)


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

@auth.requires_login()
def test_user_setting():
    form = user_setting(auth.user_id)
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    photo_url = get_user_photo_url(userrev.email)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'index'))
    return dict(form=form,photo_url=photo_url)

@auth.requires_login()
def test_user_setting_photo():
    form = user_setting_photo(auth.user_id)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'index'))
    return dict(form=form)
#########################################################
#########################################################
#########################################################  




#Show user information, 
#including list of complete circuit
def show_user(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    #linktable_ref = db(db.linktable.user_id == auth.user_id).select()
    circuit_tag_table = db(db.circuit_tag_table.user_id == user_id).select()
    return dict(userrev=userrev,circuit_tag_table=circuit_tag_table)

def get_circuit(circuit_id):
    circuit = db(db.circuit.id == circuit_id).select().first()
    return circuit

def get_exercise_set(exercise_set_name):
    exercise_set = db(db.exercise_set.set_name == exercise_set_name).select()
    return exercise_set

def get_exercise(exercise_id):
    exercise = db(db.exercise.id == exercise_id).select().first()
    return exercise

def get_exercise_name(exercise_id):
    exercise = db(db.exercise.id == exercise_id).select()
    return exercise.name

#Call when user complete circuit
#Increase user's point and add circuit to list of completed 
def complete_circuit(user_id,circuit_id):
    cir = db(db.circuit.id == circuit_id).select().first()
    userrev = db(db.auth_user.id == user_id).select().first()    
    if cir is None:
        return False
    if userrev is None:
        return False    
    point = cir.point
    #newpoint = int(cir.point)
    oldpoint = userrev.point
    newpoint = oldpoint + point
    userrev.update_record(point=newpoint)
    db.circuit_tag_table.insert(user_id = auth.user_id,circuit_id = cir.id,circuit_count=1,created_on=datetime.utcnow())
    return True

#When user want to reset point
#Reset user's point and remove all completed circuit
def reset_point(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    if userrev is None:
        return False
    userrev.point = 0
    userrev.update_record()
    db(db.circuit_tag_table.user_id == userrev).delete()
    return True

#When user want to upgrade to Admin role
#Return True: success
#False: is already admin
def upgrade(user_id):
    isAd = isAdmin(user_id)
    if isAd:
        return False    
    myadmin = db(db.auth_group.role == "myadmin").select().first()
    db.auth_membership.insert(user_id = user_id,group_id = myadmin.id)
    return True

#Check if user is Admin
def isAdmin(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    myadmin = db(db.auth_group.role == "myadmin").select().first()
    exist_data = db((db.auth_membership.user_id==userrev) & (db.auth_membership.group_id == myadmin)).select().first()    
    if exist_data is not None:
        return True
    else:
        return False

#Use facebook login - Not using right now
def login_with_facebook():
    #auth.settings.login_form = FaceBookAccount()
    return dict(form = auth.login())

#When user want to add a friend
#Return True: success
#False: is already friend
def add_friend(from_user_id,to_user_id):
    if isFriend(from_user_id,to_user_id):
        return False
    db.friend_table.insert(from_user_id=from_user_id,to_user_id=to_user_id,created_on=datetime.utcnow())
    return True

#Check if one user is friend with another
def isFriend(from_user_id,to_user_id):
    fromIdObj = db(db.auth_user.id == from_user_id).select().first()
    toIdObj = db(db.auth_user.id == to_user_id).select().first()
    exist_data = db((db.friend_table.from_user_id==fromIdObj) & (db.friend_table.to_user_id == toIdObj)).select().first()
    if exist_data is not None:
        return True
    else:
        return False
#When user want to list all friend    
def show_all_friend(user_id):
    friendlist = db(db.friend_table.from_user_id == user_id).select(orderby=~db.friend_table.created_on)
    return friendlist

#When user want to see all user
def show_all_user():
    userlist = db().select(db.auth_user.ALL, orderby=db.auth_user.id)    
    return userlist

#When user want to edit setting
def user_setting(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    form = SQLFORM(db.auth_user, record=userrev,showid=False,
                   fields = ['first_name','last_name','email','password','gender','birthday'])
    
    return form

#When user want to edit photo
def user_setting_photo(user_id):
    userrev = db(db.auth_user.id == user_id).select().first()
    user_photo = db(db.user_photo.user_id == userrev).select().first()
    if user_photo is None:
        return None
    form2 = SQLFORM(db.user_photo, record=user_photo,showid=False,
                   fields = ['cached_url'])
    return form2



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

            return dict(success=success,today_circuit=today_circuit,
                firstname=auth.user.first_name,lastname=auth.user.last_name)

        if args[0] == 'logout':
            logger.info('Logging out')
            #logger.info(request.env.http_authorization)
            #auth.basic()

            #logger.info(auth.user)
            if auth.user:
                auth.logout()
            
            success=check_access()
            return dict(success=success)

        if args[0] == 'get_today_circuit':
            logger.info('get_today_circuit')
            #logger.info(request.env.http_authorization)
            auth.basic()
            result = None
            #logger.info(auth.user)
            if auth.user:
                result = get_today_circuit(auth.user.id)
                logger.info(result)
            return dict(result=result)

        else:
            patterns = 'auto'
            parser = db.parse_as_rest(patterns,args,vars)


            if parser.status == 200:
                return dict(content=parser.response)
            else:
                raise HTTP(parser.status,parser.error)
    
    #auth.settings.allow_basic_login = True
    #@auth.requires_login()
    #def POST(table_name,**vars):
    def POST(*args,**vars):
        if args[0] == 'get_upload_url':
            logger.info('getting post get upload')
            auth.basic()
            if check_access():
                #logger.info(request.env.http_authorization)
                #logger.info(auth.user)
                upload_url = get_upload_url(auth.user)
                return dict(upload_url=upload_url['upload_url'])
            else:
                return dict(upload_url=None, error="Auth error")

        if args[0] == 'get_user_photo_url':
            logger.info('get_user_photo_url')
            post_vars = request.body.read()
            logger.info(post_vars)
            post_vars = json.loads(post_vars)
            logger.info(post_vars)
            logger.info(post_vars['email'])

            #logger.info(request.env.http_authorization)
            auth.basic()
            result = None
            #logger.info(auth.user)
            if auth.user:
                result = {}
                if len(vars) == 1:
                    email = post_vars['email']
                    cached_url = get_user_photo_url(email)
                    result[email] = cached_url
                    #result.append(dict(email=cached_url))
                else:
                    for email in post_vars['email']:
                        cached_url = get_user_photo_url(email)
                        result[email] = cached_url
                        #result.append(dict(email=cached_url))

            logger.info(result)
            return dict(result=result)

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
    make_today_circuit(user_id);
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


def get_upload_url(auth_user):
    from google.appengine.ext import blobstore
    upload_url = blobstore.create_upload_url(URL('return_upload', vars=dict(user_id=auth_user.id)))
    return dict(upload_url=upload_url)

def return_upload():
    from google.appengine.ext import blobstore
    from google.appengine.api import images

    blob_info = blobstore.parse_blob_info(request.vars.content)
    blob_key = blob_info.key()
    cached_url = images.get_serving_url(blob_key)
    original_filename = blob_info.filename
    logger.info(blob_key)
    logger.info(original_filename)

    db.user_photo.update_or_insert(db.user_photo.user_id==request.vars.user_id,user_id=request.vars.user_id,
        blob_key=blob_key,original_filename=original_filename,cached_url=cached_url)

    return cached_url

def get_user_photo_url(email):
    logger.info(email)
    user_id = db(db.auth_user.email == email).select().first()['id']
    logger.info(user_id)
    cached_url = db(db.user_photo.user_id == user_id).select().first()['cached_url']
    logger.info(cached_url)

    return cached_url



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
