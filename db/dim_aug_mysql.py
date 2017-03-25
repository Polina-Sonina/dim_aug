import os, io
import pymysql

DBNAME = 'dim_aug'
DBSCHEMA = 'dim_aug_schema.sql'
datafile = 'aug_dim_tab.txt'
DBHOST = 'localhost'
DBUSER = 'root'
DBPASSWD = 'password'
DBPORT = 3306

def file_to_list(file_name):
    fr = io.open(file_name, encoding = 'utf-8')
    l = [line.strip().split('\t') for line in fr]
    print(l[0][1])
    l.sort(key = lambda line: line[1].lower())
    l.sort(key = lambda line: line[5].lower())
    fr.close()
    return l

def get_data(l):
    lexems, lemmas = [], []
    j = 0
    for i in range(len(l)):
        lem = l[i]
        if lem[5] not in lexems:
            j += 1
            lexems.append(lem[5])
            lemmas.append((lem[0], lem[1], lem[2], lem[3], lem[4], j))
        else:
            lex_index = lexems.index(lem[5]) + 1
            lemmas.append((lem[0], lem[1], lem[2], lem[3], lem[4], lex_index))
    return lexems, lemmas

def create_db(dbname, schemafile):

    with pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWD,charset="utf8",port=DBPORT) as conn:
        conn.execute('DROP DATABASE IF EXISTS '+dbname+';')
        conn.execute('CREATE DATABASE '+dbname+' DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;;')
        print('creating schema')
        schema = None
        with open(schemafile, 'rt') as f:
            schema = f.read()
        if schema is not None:
            conn.execute('USE  '+dbname+';')
            conn.execute(schema)
        print('schema created successfully')
        conn.close()
    return True

def fill_db(dbname, lexemes, lemmas):
    with pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWD,db=dbname,charset="utf8",port=DBPORT) as conn:
        print('filling database...')
        conn.executemany('insert into Lexeme(lexid, lex) values (null, %s)', lexemes)  
        conn.executemany('insert into Lemma(lemid, lemtype, lem, suffix, tag, descr, lexid) values (null, %s, %s, %s, %s, %s, %s)', lemmas)    
        conn.close()
        
def query_db(dbname):
    with pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWD,db=dbname,charset="utf8",port=DBPORT) as conn:
        print('querying database...')

        print('--- Lexeme:')
        conn.execute('select * from Lexeme LIMIT 5;')
        for row in conn.fetchall():
            lexid, lex = row
            print(lexid, lex)
        
        print('--- Lemma:')
        conn.execute('select * from Lemma LIMIT 5;')
        for row in conn.fetchall():
            lemid, lemtype, lem, suffix, tag, descr, lexid = row
            print(lemid, lemtype, lem, suffix, tag, descr, lexid) 

        for row in conn.fetchall():
            lem, lex = row
            print(lex, lem) 
        conn.close()

        
if __name__ == '__main__':
    
    l = file_to_list(datafile)
    lexemes, lemmas = get_data(l)
    
    # --- prepare DB
    create_db(DBNAME, DBSCHEMA)
    fill_db(DBNAME, lexemes, lemmas)

    # --- query DB
    query_db(DBNAME)
