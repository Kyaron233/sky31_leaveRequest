import mysql.connector
from flask import current_app

def get_connection():
    connection = mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        charset=current_app.config['MYSQL_CHARSET'],
        autocommit=current_app.config['MYSQL_AUTOCOMMIT']
    )
    return connection