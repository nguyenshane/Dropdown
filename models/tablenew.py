# -*- coding: utf-8 -*-
UNITS = ['','sets','minutes','seconds']


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
                Field('point', 'integer'),
                Field('count','integer'),
                Field('unit', length=255), fake_migrate=True)


db.circuit.unit.requires = IS_IN_SET(UNITS, zero=None)
db.circuit.exercise_set_name.requires = IS_IN_DB(db,'exercise_set.set_name',multiple=False)

db.define_table('linktable',
                Field('user_id','reference auth_user'),
                Field('exercise_id','reference exercise'),
                Field('exercise_name'))

db.define_table('daily',
                Field('user_id','reference auth_user'),
                Field('circuit_id','reference exercise'))
