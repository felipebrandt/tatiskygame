from peewee import *
from os import getenv

BASE = ''


if BASE == 'nuvem':
    db = PostgresqlDatabase(database=getenv('DATABASE', 'defaultdb'),
                            host=getenv('HOST', 'linkimovel-brain-ag.l.aivencloud.com'),
                            port=getenv('PORT', '21242'),
                            user=getenv('USER', 'avnadmin'),
                            password=getenv('PASSWORD', 'AVNS_FLSIPqCapJPjpvmSHTG'))
else:
    db = MySQLDatabase(database=getenv('DATABASE', ''),
                       host=getenv('HOST', ''),
                       port=int(getenv('PORTS', 13046)),
                       user=getenv('USER', ''),
                       password=getenv('PASSWORD', ''),
                       ssl={'ca': 'ca.pem'})