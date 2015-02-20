# -*- coding: utf-8 -*-


db.define_table('exercise',
                Field('name', unique=True),
                Field('point', 'integer'),
                Field('demopic','upload'),
                Field('body', 'text'))

db.define_table('linktable',
                Field('user_id','reference auth_user'),
                Field('exercise_id','reference exercise'),
                Field('exercise_name'))
