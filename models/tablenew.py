# -*- coding: utf-8 -*-
from datetime import datetime

UNITS = ['','sets','minutes','seconds']

db.define_table('user_photo',
                #Field('content', 'upload'),
                Field('blob_key'),
                Field('original_filename'),
                Field('cached_url', 'text'),
                Field('user_id','reference auth_user'), fake_migrate=True)
db.user_photo.blob_key.readable = db.user_photo.blob_key.writable = False
db.user_photo.original_filename.readable = db.user_photo.original_filename.writable = False


db.define_table('exercise',
                Field('name', unique=True, length=255, label='Exercise name'),
                Field('demopic', unique=True, length=255, label='Photo filename'),
                Field('body', 'text', label='Description'), fake_migrate=True)

db.define_table('exercise_set',
		Field('set_name', length=255),
                Field('exercise_id','reference exercise'),
                Field('point', 'integer'),
                Field('count','integer'),
                Field('unit', length=255), migrate=True)

db.exercise_set.unit.requires = IS_IN_SET(UNITS, zero=None)
db.exercise_set.exercise_id.requires = IS_IN_DB(db,'exercise.id',multiple=False)

db.define_table('circuit',
		Field('circuit_name', unique=True, length=255),
                Field('exercise_set_name', length=255),
                Field('main', 'boolean'),
                Field('point', 'integer'),
                Field('count','integer'),
                Field('unit', length=255), fake_migrate=True, format='%(circuit_name)s')

db.circuit.unit.requires = IS_IN_SET(UNITS, zero=None)
db.circuit.exercise_set_name.requires = IS_IN_DB(db,'exercise_set.set_name',multiple=False)

db.define_table('linktable',
                Field('user_id','reference auth_user'),
                Field('exercise_id','reference exercise'),
                Field('exercise_name'))

db.define_table('daily',
                Field('user_id','reference auth_user', label='User'),
                Field('circuit_id','reference circuit', label='Circuit'), 
                Field('created_on','datetime', label='Date Created', default=datetime.utcnow()), fake_migrate=True)
db.daily.circuit_id.requires = IS_IN_DB(db,'circuit.id','%(circuit_name)s',multiple=False)
db.daily.created_on.represent = lambda value, row: value.strftime("%m/%d/%Y")
db.daily.created_on.writable = False

db.define_table('test_create_table',
                Field('user_id','reference auth_user', label='User'),
                Field('circuit_id','reference circuit', label='Circuit'),
                Field('circuit_count','integer'),
                Field('created_on','datetime', label='Date Created', default=datetime.utcnow()), fake_migrate=True)
db.daily.circuit_id.requires = IS_IN_DB(db,'circuit.id','%(circuit_name)s',multiple=False)
db.daily.created_on.represent = lambda value, row: value.strftime("%m/%d/%Y")
db.daily.created_on.writable = False


db.define_table('circuit_tag_table',
                Field('user_id','reference auth_user', label='User'),
                Field('circuit_id','reference circuit', label='Circuit'),
                Field('circuit_count','integer'),
                Field('from_user_id','reference auth_user'),
                Field('created_on','datetime', label='Date Created', default=datetime.utcnow()), fake_migrate=True)
db.circuit_tag_table.circuit_id.requires = IS_IN_DB(db,'circuit.id','%(circuit_name)s',multiple=False)
db.circuit_tag_table.created_on.represent = lambda value, row: value.strftime("%m/%d/%Y")
db.circuit_tag_table.created_on.writable = False



db.define_table('friend_table',
                Field('from_user_id','reference auth_user', label='From User'),
                Field('to_user_id','reference auth_user', label='To User'),
                Field('circuit_id','reference circuit', label='Throwdown'),
                Field('has_throwdown','boolean', label='Has Throwdown'),
                Field('created_on','datetime', label='Date Added', default=datetime.utcnow()), fake_migrate=True)
db.friend_table.created_on.represent = lambda value, row: value.strftime("%m/%d/%Y")
db.friend_table.created_on.writable = False

db.define_table('dropdown_table',
                Field('from_user_id','reference auth_user', label='From User'),
                Field('to_user_id','reference auth_user', label='To User'),
                Field('circuit_id','reference circuit', label='Circuit'),
                Field('isComplete','boolean', label='Completed'),
                Field('created_on','datetime', label='Date Added', default=datetime.utcnow()), fake_migrate=True)
db.dropdown_table.created_on.represent = lambda value, row: value.strftime("%m/%d/%Y")


#####################

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
