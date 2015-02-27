# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import random
from gluon.serializers import json
from google.appengine.ext import blobstore
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
    
    # lastExercise = db.exercise.last()
    # maxNum = lastExercise.id;
    
    # num1 = random.randint(1, maxNum)
    # num2 = random.randint(1, maxNum)
    # num3 = random.randint(1, maxNum)
    # while(num2 == num1 or num2 == num3):
    #     num2 = random.randint(1, maxNum)
    # while(num3 == num1 or num3 == num2):
    #     num3 = random.randint(1, maxNum)
        
    # exercise = (db.exercise.id ==num1 ) | (db.exercise.id ==num2) | (db.exercise.id ==num3)

    exercise = db().select(db.exercise.ALL, orderby='<random>', limitby=(0,2))

    #exercise = db.executesql('SELECT * FROM exercise ORDER BY RAND() LIMIT 1')

    logger.info(exercise)


    def generate_complete_button(row):
        b = A('Complete', _class='btn', _href=URL('admin', 'complete', args=[row.id]))
        return b
    
    links = [
        dict(header='', body = generate_complete_button),
        ]
    

    grid = SQLTABLE(exercise)
    return dict(grid=grid)

    #return locals()

def daily_circuit_manager():
    table = SQLFORM.grid(db.daily)
    return dict(table=table)

def create_daily_circuit():

    if not request.args(0):
        def generate_buttons(row):
            # If the record is ours, we can edit/delete it. If not, view only
            b = ''
            #b = A('View', _class='btn', _href=URL('default', 'view', args=[row.id]))
            b = A('View Circuit', _class='btn', _href=URL('admin', 'daily_circuit_manager', user_signature=True, vars=dict(keywords='daily.user_id='+str(row.id))))
            b += ' '
            b += A('Make New Circuit', _class='btn btn-warning', _href=URL('admin', 'create_daily_circuit', user_signature=True, args=['make',row.id]))
            return b

        # Creates extra buttons.
        links = [
            dict(header='', body = generate_buttons),
            ]

        table = SQLFORM.grid(db.auth_user,
            fields=[db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email],
            editable=False, deletable=False, details=False, create=False, links=links,
            paginate=10, exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False, csv=False, 
                               tsv_with_hidden_cols=False, tsv=False, json=False))
        return dict(table=table)

    if request.args(0) == 'make':
        user_id = request.args(1)
        if make_today_circuit(user_id):
            session.flash = T("New Daily Circuit created")
        else:
            session.flash = T("Error, cannot make Daily Circuit")
        redirect(URL('admin','create_daily_circuit'))

def make_today_circuit(user_id):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    created_on = get_date_created_circuit(user_id)
    if created_on < today:
        logger.info(del_daily_circuit(user_id))
        random_daily_circuits = get_random_daily_circuits(1,2)
        logger.info(random_daily_circuits)
        for circuit in random_daily_circuits:
            db.daily.insert(
                user_id = user_id,
                circuit_id = circuit.id, 
                created_on = today,
                )
        return True
    return False

def get_today_circuit(user_id):
    logger.info('here')
    today_circuit = db(db.daily.user_id==user_id).select()
    return today_circuit

def del_daily_circuit(user_id):
    daily_circuit = db(db.daily.user_id==user_id).delete()
    return daily_circuit

def get_date_created_circuit(user_id):
    created_on = db(db.daily.user_id==user_id).select(limitby=(0,1))

    if created_on:
        created_on = created_on[0].created_on
        created_on = created_on.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        created_on = datetime.utcnow().replace(year=2000,hour=0, minute=0, second=0, microsecond=0)
    
    return created_on


def get_random_daily_circuits(num_main, num_minor):

    main_circuits = db(db.circuit.main==True).select(orderby='<random>', limitby=(0,num_main))
    minor_circuits = db(db.circuit.main==False).select(orderby='<random>', limitby=(0,num_minor))

    selected_circuits = main_circuits & minor_circuits
    return selected_circuits


def circuit_manager():
    table = SQLFORM.grid(db.circuit)
    return dict(table=table)

def create_circuit():
    # List all of the circuits
    query = db().select(db.exercise_set.set_name, distinct=True)
    option = CAT()
    for row in query:
        exercise_name = row.set_name
        #exercise_name = db(db.exercise.id == row.exercise_id).select(db.exercise.name)[0].name
        option += OPTION(exercise_name, _value=exercise_name)

    
    form = SELECT(option, _class='generic-widget', _id='exercise_set', _name='exercise_set')
    form = FORM(form , INPUT(_type='submit'), _action='', _method='post')

    # Create exercise set based on the chosen exercises
    if form.process().accepted:
        response.cookies['create_circuit'] = form.vars.exercise_set
        response.cookies['create_circuit']['expires'] = 3600
        redirect(URL('admin','create_circuit_detail'))
        
    return dict(form=form)

def create_circuit_detail():
    multiple_sets = False
    # Get create_exercise_set from cookie
    if request.cookies.has_key('create_circuit') and not request.cookies['create_circuit'].value == '':
        exercise_sets = request.cookies['create_circuit'].value
        if (exercise_sets[0] == '['):
            exercise_sets = eval(exercise_sets)
            multiple_sets = True
    else:
        redirect(URL('admin','create_circuit'))

    # Create the form for exercise set detail
    fields = [Field('exercise_set_name', label='Exercise set', requires=IS_NOT_EMPTY(), default=exercise_sets, writable=False),
              Field('circuit_name', requires=IS_NOT_EMPTY(), default=exercise_sets),
              Field('main', 'boolean', label='Main circuit', default=False),
              Field('count', requires=IS_NOT_EMPTY(), label='Count'),
              Field('unit',  label='Unit', requires=IS_IN_SET(UNITS, zero=None, sort=False)),
              ]
    suggested_point = 0

    # case of 1 set only
    if not multiple_sets:
        _exercise_sets = db(db.exercise_set.set_name == exercise_sets).select()
        _point = 0

        for _exercise_set in _exercise_sets:
            _point += _exercise_set.point
        suggested_point += _point
    else:
        # multiple sets not allow
        logger.info("error, multiple sets not allowed")
        # for exercise_set_name in exercise_sets:
        #     _exercise_sets = db(db.exercise_set.set_name == exercise_set_name).select()
        #     _point = 0

        #     for _exercise_set in _exercise_sets:
        #         _point += _exercise_set.point
        #     suggested_point += _point

    fields += Field('point', requires=IS_NOT_EMPTY(), label='Points (' + str(suggested_point) + ')', default=suggested_point),
    #fields += Field(exercise_set_name+'name', requires=IS_NOT_EMPTY(), writable=False, label=exercise_set_name, default=""),
    
    
    form = SQLFORM.factory(
        *fields, hidden=dict(exercise_sets=exercise_sets)
    )
    


    # Add to database
    if form.process().accepted:
        form.vars.exercise_sets = request.vars.exercise_sets
        logger.info(form.vars)
        # case of 1 set only
        if not multiple_sets:
            db.circuit.insert(
                circuit_name = form.vars['circuit_name'],
                main = form.vars['main'], 
                count = form.vars['count'], 
                point = form.vars['point'], 
                unit = form.vars['unit'], 
                exercise_set_name = request.vars.exercise_sets,
                )
        else:
            # multiple sets for a circuit
            logger.info("error, multiple sets not allowed")
        
        session.flash = T("New Circuit created")
        response.cookies['create_circuit'] = ''
        response.cookies['create_circuit']['expires'] = -10

        redirect(URL('admin','create_circuit'))

    return dict(form=form)


def exercise_set_manager():
    query = db().select(db.exercise_set.set_name, distinct=True)
    links = HTML()

    if not request.args(0):
        for row in query:
            links += HTML(A(row.set_name, _class='btn', _href=URL('admin', 'exercise_set_manager', args=[row.set_name])))
            logger.info(row.set_name)


        grid = SQLTABLE(query)
        return dict(links=links)

    else:
        set_name = request.args[0].replace('_', ' ')
        table = TR(TD('Exercise'), TD('Count & Unit'), TD('Point'))

        query = db(db.exercise_set.set_name == set_name).select()

        for row in query:
            exercise_name = db(db.exercise.id == row.exercise_id).select(db.exercise.name)[0].name
            exercise_link = A(exercise_name, _href=URL('admin', 'exercise_manager/view/exercise/'+str(row.exercise_id),user_signature=True))
            table += TR(TD(exercise_link), TD(str(row.count) + ' ' + row.unit), TD(row.point))

        table = TABLE(table)

        #table = SQLTABLE(query)
        return dict(table=table)




def create_exercise_set():
    # List all of the exercises
    form = SQLFORM.factory(
        Field('exercise', requires=IS_IN_DB(db, db.exercise.id, '%(name)s', multiple=True))
        )
    # Create exercise set based on the chosen exercises
    if form.process().accepted:
        response.cookies['create_exercise_set'] = form.vars.exercise
        response.cookies['create_exercise_set']['expires'] = 3600
        redirect(URL('admin','create_exercise_set_detail'))
        
    return dict(form=form)


def create_exercise_set_detail():
    # Get create_exercise_set from cookie
    if request.cookies.has_key('create_exercise_set') and not request.cookies['create_exercise_set'].value == '':
        exercises = eval(request.cookies['create_exercise_set'].value)
    else:
        redirect(URL('admin','create_exercise_set'))

    # Create the form for exercise set detail
    fields = [Field('exercise_set_name', requires=IS_NOT_EMPTY())]

    for exercise_id in exercises:
        exercise_name = db(db.exercise.id == exercise_id).select().first().name
        fields += Field(exercise_id+'id', requires=IS_NOT_EMPTY(), writable=False, label=exercise_name, default=""),
        fields += Field(exercise_id+'count' , requires=IS_NOT_EMPTY(), label='Count'),
        fields += Field(exercise_id+'unit' ,  label='Unit', requires=IS_IN_SET(UNITS, zero=None, sort=False)),
        fields += Field(exercise_id+'point' , requires=IS_NOT_EMPTY(), label='Points'),

    form = SQLFORM.factory(
        *fields, hidden=dict(exercises=exercises)
    )

    # Add to database
    if form.process().accepted:
        exercise_set_name = form.vars['exercise_set_name']
        for exercise_id in exercises:
            db.exercise_set.insert( 
                set_name = exercise_set_name, 
                exercise_id = exercise_id, 
                count = form.vars[exercise_id+'count'], 
                point = form.vars[exercise_id+'point'], 
                unit = form.vars[exercise_id+'unit'], 
                )

        session.flash = T("New Exercise Set created")
        response.cookies['create_exercise_set'] = ''
        response.cookies['create_exercise_set']['expires'] = -10

        redirect(URL('admin','create_exercise_set'))

    return dict(form=form)



@auth.requires_login()
def showuser():
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    linktable_ref = db(db.linktable.user_id == auth.user_id).select()
    return dict(userrev=userrev,linktable_ref=linktable_ref)


def show():
    exercise = db.exercise(request.args(0,cast=int)) or redirect(URL('index'))
    point = exercise.point
    
    return dict(exercise=exercise,point=point)

@auth.requires_login()
def complete():
    
    content = None
    
    exerciseid = request.args(0)
    
    exer = db(db.exercise.id == exerciseid).select().first()
    userrev = db(db.auth_user.id == auth.user_id).select().first()
    
    point = exer.point
    newpoint = int(userrev.point)
    form2 = FORM.confirm('Did you complete this exercise')
    if form2.accepted:
        redirect(URL('default', 'showuser'))
    newpoint += point
    userrev.update_record(point=newpoint)
    
    linktable_id = db.linktable.insert(user_id = auth.user_id,exercise_id = exerciseid,exercise_name=exer.name)
    
    
    content = form2
        
    
    return dict(content=content,exer=exer,userrev=userrev)

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
def exercise_manager():
    all_exercises = SQLFORM.grid(db.exercise)
    
    # form = SQLFORM.factory(
    #     Field('name',label='Exercise Name'),
    #     Field('point','integer'),
    #     Field('count','integer'),
    #     Field('unit', requires = IS_IN_SET(UNITS, zero=None)),
    #     Field('body','text',label='Description'))
    # form.add_button('Cancel', URL('default', 'index'))
    
    # if form.process().accepted:
    #     db.exercise.insert(
    #         name=form.vars.name,
    #         point=form.vars.point,
    #         count=form.vars.count,
    #         unit=form.vars.unit,
    #         body=form.vars.body)
    #     # Successful processing.
    #     session.flash = T("New exercise created")
    #     redirect(URL('default', 'index'))
    return locals()


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




def upload():
    # As an example ONLY, we always read the item of the table with id 1.
    item = db.user_photo(request.args(0))
    upload_url = URL('download', args=request.args(0))
    if item is None:
        old_blob_key = None
        form = SQLFORM(db.user_photo, upload=upload_url, deletable=False)
    else:
        old_blob_key = item.blob_key
        form = SQLFORM(db.user_photo, record=item, upload=upload_url, deletable=False)
    # If this is a POST, stores the upload information.
    content_ok = True
    if request.env.request_method == 'POST': 
        blob_info = None
        # Checks if there is new content. 
        if request.vars.content is not None and request.vars.content != '':
            # Decodes the new content.
            try:
                blob_info = blobstore.parse_blob_info(request.vars.content)
            except Exception, e:
                # If the file is missing, in appengine (as opposed to the development
                # environment) we get a request.vars.content with a special structure.
                # Tries to detect it.
                if ('Content-Length: 0\r\n' in request.vars.content and
                    'filename=""\r\n' in request.vars.content):
                    # Nothing was uploaded.
                    blob_info = None
                else:
                    # We really don't know how to make sense of this.
                    blob_info = None
                    content_ok = False
            if blob_info != None:
                # Checks that the upload succeeded.
                if blob_info.size == 0:
                    content_ok = False
                    blobstore.delete(blob_info.key())
                else:
                    form.vars.blob_key = blob_info.key()
                    try:
                        form.vars.original_filename = request.vars.content.filename
                    except Exception, e:
                        content_ok = False
                        blobstore.delete(blob_info.key())
                        
        # Checks if a deletion has been requested without new content.
        if blob_info is None and request.vars.content__delete == 'on':
            form.vars.original_filename = None
            form.vars.blob_key = None
            form.vars.content = None

    # Form processing.
    if form.process(onvalidation=process_upload_form(content_ok)).accepted:

        # Deletes the content field, in case the attachment has been deleted.
        if (request.vars.content__delete == 'on' and blob_info is None):
            db(db.user_photo.id == form.vars.id).update(
                content = None,
                blob_key = None, 
                original_filename = None)

        if request.vars.content__delete == 'on' and blob_info is None:
            session.flash = T('The attached file has been deleted.')
        else:
            if form.vars.blob_key == old_blob_key:
                if old_blob_key is None:
                    session.flash = T('No file has been uploaded.')
                else:
                    session.flash = T('Your attached file has been left unchanged.')
            else:
                if form.vars.blob_key is None:
                    session.flash = T('Your attached file has been left unchanged.')
                else:
                    session.flash = T('Attached file updated.')
            
        # For demo only, we go back to where we were.
        raise HTTP(303, Location=URL('upload', args=[form.vars.id]))
    
    elif form.errors:
        # There was an error, let's delete the newly uploaded content.
        if blob_info != None:
            blobstore.delete(blob_info.key())
    
    # Produces an upload URL.
    upload_url = blobstore.create_upload_url(URL('upload', args=request.args))
    form['_action'] = upload_url
    return dict(form=form)


def process_upload_form(content_ok):
    def f(form):
        if not content_ok:
            form.errors.content = T('File upload error')
            return
    return f


def download():
    item = db.user_photo(request.args(0))
    if item is None:
        raise HTTP(404, "Not found")
    filename = item.original_filename or 'file'
    if item.blob_key is None:
        response.headers['Content-Disposition'] = 'attachment; filename="none"'
        import StringIO
        return response.stream(StringIO.StringIO(''), chunk_size=1024)
    blob_info = blobstore.get(item.blob_key)
    if blob_info is None:
        #This being appengine, we need to try again.
        blob_info = blobstore.get(item.blob_key)
        if blob_info is None:
            raise HTTP(503, "Temporarily unavailable; try again later.")
    response.headers['X-AppEngine-BlobKey'] = item.blob_key;
    response.headers['Content-Type'] = blob_info.content_type;
    response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename.replace('"', '\"').replace(' ', '_')
    return response.body.getvalue()






