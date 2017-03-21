import os
import pymysql
from flask import Flask, render_template, request, flash, redirect
from flaskext.mysql import MySQL

dbname = 'dim_aug'

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '4273'
app.config['MYSQL_DATABASE_DB'] = dbname
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

def file_to_list(file_name):
    fr = open(file_name, encoding = 'utf-8')
    l = [line.strip() for line in fr]
    fr.close()
    return l

def search_by_lem(dbname, lemma):
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
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
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
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
def root():
    return redirect('/index')

@app.route('/index')
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

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
        result = request.form
        suffix = request.form.getlist('suffix')
        suf_meaning = request.form.getlist('suf_meaning')
        lemma = ''
        if 'lem' in result:
            lemma = result['lem']
            form = search_by_lem(dbname, lemma)
            return render_template("result.html", lemma = lemma, form = form)
        else:
            lexeme = result['lex']
            lemtype = 'all'
            if 'lemtype' in result:
                lemtype = result['lemtype']
            dim, aug = search_by_lex(dbname, lexeme, lemtype, suffix, suf_meaning)
            return render_template("result.html", lemma = lemma, lexeme = lexeme, dim = dim, aug = aug)  
 
if __name__ == "__main__":
    app.run()
