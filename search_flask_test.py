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

def search_by_lem(dbname, lemma):
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
        conn.execute(
            '''SELECT Lemma.lemtype, Lexeme.lex, Lemma.suffix, Lemma.tag
                FROM Lemma
                JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                WHERE Lemma.lem = %s;
                ''', lemma)
        form = conn.fetchall()
        conn.close()
        return form

def search_by_lex(dbname, lexeme, lemtype = 'all'):
    with pymysql.connect(host='localhost',port=3306,user='root',passwd='4273',db=dbname,charset="utf8") as conn:
        if lemtype == 'd':
            conn.execute(
                '''SELECT Lemma.lem, Lemma.suffix, Lemma.tag
                    FROM Lemma
                    JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                    WHERE Lexeme.lex = %s AND Lemma.lemtype = 'd';
                    ''', lexeme)
            dim = conn.fetchall()
            aug = ()
        elif lemtype == 'a':
            conn.execute(
                '''SELECT Lemma.lem, Lemma.suffix, Lemma.tag
                    FROM Lemma
                    JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                    WHERE Lexeme.lex = %s AND Lemma.lemtype = 'a';
                    ''', lexeme)
            aug = conn.fetchall()
            dim = ()
        else:
            conn.execute(
                '''SELECT Lemma.lem, Lemma.suffix, Lemma.tag
                    FROM Lemma
                    JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                    WHERE Lexeme.lex = %s AND Lemma.lemtype = 'd';
                    ''', lexeme)
            dim = conn.fetchall()
            conn.execute(
                '''SELECT Lemma.lem, Lemma.suffix, Lemma.tag
                    FROM Lemma
                    JOIN Lexeme ON Lexeme.lexid = Lemma.lexid
                    WHERE Lexeme.lex = %s AND Lemma.lemtype = 'a';
                    ''', lexeme)
            aug = conn.fetchall()
        conn.close()
        return dim, aug

@app.route('/')
def root():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
        result = request.form
        lemma = ''
        if 'lem' in result:
            lemma = result['lem']
            form = search_by_lem(dbname, lemma)
            print(form)
            return render_template("result.html", lemma = lemma, form = form)
        else:
            lexeme = result['lex']
            lemtype = 'all'
            if 'lemtype' in result:
                lemtype = result['lemtype']
            dim, aug = search_by_lex(dbname, lexeme, lemtype)
            print(dim)
            print(aug)
            return render_template("result.html", lemma = lemma, lexeme = lexeme, dim = dim, aug = aug)  
 
if __name__ == "__main__":
    app.run()
