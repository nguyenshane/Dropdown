# -*- coding: utf-8 -*-
from datetime import datetime
import string
import random
'''
db.define_table('player',
                Field('email'),
                Field('created_on', 'datetime'),
                Field('donation', default=0),
                )

db.player.email.requires = IS_NOT_IN_DB(db, 'player.email')
db.player.email.requires = IS_NOT_EMPTY()
db.player.email.requires = IS_EMAIL()
db.player.created_on.readable = db.player.created_on.writable = False
db.player.donation.readable = db.player.donation.writable = False


db.define_table('ticket',
                Field('player_id', 'reference player'),
                Field('ticket_number'),
                )
'''
def get_random():
    size=6
    chars=string.ascii_uppercase + string.digits
    randomstr=''
    while True:
        randomstr = ''.join(random.choice(chars) for _ in range(size))
        if db(db.ticket.ticket_number == randomstr).select().first() == None:
            break
    return randomstr