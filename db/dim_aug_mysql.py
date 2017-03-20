import os
import pymysql

DBNAME = 'dim_aug'
DBSCHEMA = 'dim_aug_schema.sql'
datafile = 'aug_dim_tab.txt'

def file_to_list(file_name):
    fr = open(file_name, encoding = 'utf-8')
    l = [line.strip().split('\t') for line in fr]
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
    print('create db:', dbname)

    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
        conn.execute('DROP DATABASE IF EXISTS dim_aug;')
        conn.execute('CREATE DATABASE IF NOT EXISTS dim_aug;')
        print('creating schema')
        schema = None
        with open(schemafile, 'rt') as f:
            schema = f.read()
            
        if schema is not None:
            conn.execute('USE dim_aug;')
            conn.execute(schema)
        print('schema created successfully')
        conn.close()
    return True

def fill_db(dbname, lexemes, lemmas):
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
        print('filling database...')
        conn.executemany('insert into Lexeme(lexid, lex) values (null, %s)', lexemes)  
        conn.executemany('insert into Lemma(lemid, lemtype, lem, suffix, tag, descr, lexid) values (null, %s, %s, %s, %s, %s, %s)', lemmas)    
        conn.close()
        
def query_db(dbname):
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
        print('querying database...')

        print('--- Lexeme:')
        conn.execute('select * from Lexeme LIMIT 10;')
        for row in conn.fetchall():
            lexid, lex = row
            print(lexid, lex)
        
        print('--- Lemma:')
        conn.execute('select * from Lemma LIMIT 10;')
        for row in conn.fetchall():
            lemid, lemtype, lem, suffix, tag, descr, lexid = row
            print(lemid, lemtype, lem, suffix, tag, descr, lexid) 
            
        print('--- Lexeme - Lemma LIMIT 10:')
        conn.execute(
            '''select Lemma.lem, Lexeme.lex
                from Lemma
                natural join Lexeme
                LIMIT 10;
                ''')
        for row in conn.fetchall():
            lem, lex = row
            print(lex, lem) 

        print('--- Lemma by Lexeme:')
        conn.execute(
            '''SELECT Lemma.lem, Lemma.suffix, Lemma.tag, Lexeme.lex
                FROM Lemma
                JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                WHERE Lexeme.lex = "баба";
                ''')
        for row in conn.fetchall():
            lem, suffix, tag, lex = row
            print(lex, lem, suffix, tag) 
        conn.close()

        
if __name__ == '__main__':
    
    l = file_to_list(datafile)
    lexemes, lemmas = get_data(l)
    
    # --- prepare DB
    create_db(DBNAME, DBSCHEMA)
    fill_db(DBNAME, lexemes, lemmas)

    # --- query DB
    query_db(DBNAME)
