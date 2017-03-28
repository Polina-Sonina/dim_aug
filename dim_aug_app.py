import os
from flask import Flask, render_template, request, flash, redirect
import pymysql

DBNAME = 'dim_aug'
DBHOST = 'localhost'
DBUSER = 'root'
DBPASSWD = 'password'
DBPORT = 3306

app = Flask(__name__)

def file_to_list(file_name):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    file_url = os.path.join(SITE_ROOT, 'static', file_name)    
    with open(file_url, encoding='utf-8') as fr:
        l = [line.strip() for line in fr]
        fr.close()
    return l

def search_by_lem(dbname, lemma):
    with pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWD,db=dbname,charset="utf8",port=DBPORT) as conn:
        conn.execute(
            '''SELECT Lemma.lemtype, Lexeme.lex, Lemma.suffix, Lemma.tag, Lemma.descr
                FROM Lemma
                JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                WHERE Lemma.lem = %s;
                ''', lemma)
        form = conn.fetchall()
        conn.close()
        return form

def search_by_lex(dbname, lexeme, lemtype, suffix, suf_meaning):
    with pymysql.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWD,db=dbname,charset="utf8",port=DBPORT) as conn:
        sql = '''SELECT Lemma.lem, Lexeme.lex, Lemma.suffix, Lemma.tag, Lemma.descr
                    FROM Lemma
                    JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                    WHERE '''
        if lexeme != '':
            sql += "Lexeme.lex = '" + lexeme + "' AND "
            
        if suffix != []:
            suf_sql = []
            for i in range(len(suffix)):
                suf_sql.append("Lemma.suffix = '" + suffix[i] + "'")
            sql += "(" + " OR ".join(suf_sql) + ") AND "

        if suf_meaning != []:
            suf_meaning_sql = []
            for i in range(len(suf_meaning)):
                suf_meaning_sql.append("Lemma.tag = '" + suf_meaning[i] + "'")
            sql += "(" + " OR ".join(suf_meaning_sql) + ") AND "
            
        if lemtype == 'd':
            conn.execute(sql + "Lemma.lemtype = 'd';")
            dim = conn.fetchall()
            aug = ()
        elif lemtype == 'a':
            conn.execute(sql + "Lemma.lemtype = 'a';")
            aug = conn.fetchall()
            dim = ()
        else:
            conn.execute(sql + "Lemma.lemtype = 'd';")
            dim = conn.fetchall()
            conn.execute(sql + "Lemma.lemtype = 'a';")
            aug = conn.fetchall()
        conn.close()
        return dim, aug

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search',methods = ['GET'])
def search():
    suffixes_d = file_to_list('suffixes_d.txt')
    suf_meanings_d = file_to_list('suf_meanings_d.txt')
    suffixes_a = file_to_list('suffixes_a.txt')
    suf_meanings_a = file_to_list('suf_meanings_a.txt')
    return render_template('search.html', suffixes_d = suffixes_d, suf_meanings_d = suf_meanings_d,
                           suffixes_a = suffixes_a, suf_meanings_a = suf_meanings_a)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/exercises')
def exercises():
    return render_template('exercises.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        lemma = ''
        if 'lem' in result:
            lemma = result['lem']
            form = search_by_lem(DBNAME, lemma)
            if form == ():
                lemma = ' '
            return render_template("result.html", lemma = lemma, form = form)
        else:
            lexeme = result['lex']
            lemtype = 'all'
            suffix = request.form.getlist('suffix')
            suf_meaning = request.form.getlist('suf_meaning')            
            if 'lemtype' in result:
                lemtype = result['lemtype']
            dim, aug = search_by_lex(DBNAME, lexeme, lemtype, suffix, suf_meaning)
            return render_template("result.html", lemma = lemma, lexeme = lexeme, dim = dim, aug = aug)  
 
if __name__ == "__main__":
    app.run()

