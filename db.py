# -*- coding: utf-8 -*-

'''
create table contract_content(
    id int not null auto_increment primary key,
    contract_id varchar(100) not null,
    contract_name varchar(100) not null,
    party_a varchar(100) not null,
    party_b varchar(100) not null,
    content varchar(1000) not null
);
'''

import mysql.connector      # pip install mysql-connector
import util

config = util.get_config()
USER = config["user"]
PASSWORD = config["password"]
DATABASE = config["database"] 

def get_connect():
    conn = mysql.connector.connect(user=USER, password=PASSWORD, database=DATABASE)    
    return conn

def save_contract(contract_name, contract_id, party_a, party_b, content):
    # calculate the contract_id
    #contract_id = util.get_id(username, contract_name)
    try:
        sql = "insert into contract_content(contract_name, contract_id, party_a, party_b, content)" + \
            "values(%s, %s, %s, %s, %s)"
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(sql, (contract_name, contract_id, party_a, party_b, content))
        conn.commit()
    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
    return True

def getConctracList():
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute('select contract_id, contract_name, party_a, party_b from contract_content order by id desc')
        contracts = cursor.fetchall()
    except Exception as e:
        print(e)        
    finally:
        cursor.close()
        conn.close()
    return contracts

def getContent(contract_id):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute('select contract_id, contract_name, party_a, party_b, content from contract_content where contract_id=\''+contract_id+'\'')
        res = cursor.fetchall()
    except Exception as e:
        print("error!!!!!!!!!!!!!!!!!!!!!!")
        print(e)
    finally:
        cursor.close()
        conn.close()
    return res[0]