# -*- coding:utf-8 -*-
'''所有的导入包'''
import os
import re
import sqlite3

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)

from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

app = Flask(__name__)

# 从flaskr.py文件加载config
app.config.from_object(__name__)

# 从环境变量加载默认配置并覆盖config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='',
    UID=''
))

# 开启调试
# app.debug = True

# 设置一个名为FLASKR_SETTINGS的环境变量来设定一个配置文件载入后是否覆盖默认值
# silent静默开关表示flask不去关心这个键值是否存在。
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    '''建立数据库连接'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    '''初始化数据库'''
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    '''连接数据库'''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    '''关闭数据库连接'''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.before_request
def before_request():
    '''解决找不到数据库的问题'''
    g.db = connect_db()


@app.route('/')
def show_entries():
    '''根路径url/'''
    # 查询语句
    cur = g.db.execute(
        'select uid, create_time, title, text from entries order by id desc')
    # 列表生成式
    # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    entries = []
    for uid, create_time, title, text in cur.fetchall():
        username = g.db.execute(
            'select username from userinfo where id=?', [uid]).fetchall()
        entries.append(
            dict(
                username=username,
                create_time=create_time,
                title=title,
                text=text
            )
        )
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    '''发表评论'''
    # 判断是否有登录信息
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (uid, title, text) values (?, ?, ?)', [
                 app.config['UID'], request.form['title'], request.form['text']])
    g.db.commit()
    # 会乱码，解码为utf-8
    msg = ('%s发表成功！' % app.config['USERNAME']).decode('utf-8')
    flash(msg)
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''登录'''
    error = None
    if request.method == 'POST':
        # 向数据库查询账户是否存在
        cur = g.db.execute('select id,username, password from userinfo where username=? and password=?', [
                           request.form['username'], request.form['password']]).fetchall()
        # 不允许使用除字母数字下划线之外的字符作为账号
        username = re.findall(u'([0-9a-zA-Z_]+)', request.form['username'])
        password = re.findall(u'([0-9a-zA-Z_]+)', request.form['password'])
        if username and password:
            if username[0] == request.form['username'] and password[0] == request.form['password']:
                if len(request.form['username']) >= 4 and len(request.form['password']) >= 4:
                    # 判断用户名和密码是否正确
                    if not cur:
                        error = '用户名或密码不正确'.decode('utf-8')
                    else:
                        session['logged_in'] = True
                        app.config['USERNAME'] = cur[0][1]
                        app.config['UID'] = cur[0][0]
                        msg = '登录成功！'.decode('utf-8')
                        flash(msg)
                        return redirect(url_for('show_entries'))

                msg = '请输入4~16位字符!'.decode('utf-8')
                flash(msg)
                return redirect(url_for('login'))

        msg = '不允许使用除字母数字下划线之外的字符!'.decode('utf-8')
        flash(msg)
        return redirect(url_for('login'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''注册'''
    error = None
    # 判断是请求页面，还是确认注册
    if request.method == 'POST':
        # 不允许使用除字母数字下划线之外的字符作为账号
        username = re.findall(u'([0-9a-zA-Z_]+)', request.form['username'])
        password = re.findall(u'([0-9a-zA-Z_]+)', request.form['password'])
        if username and password:
            if username[0] == request.form['username'] and password[0] == request.form['password']:
                if len(request.form['username']) >= 4 and len(request.form['password']) >= 4:
                    # 向数据库查询账户是否存在
                    cur = g.db.execute('select username, password from userinfo where username=? and password=?', [
                        request.form['username'], request.form['password']])
                    # 判断是否是注册请求
                    if not cur.fetchall():
                        # 向数据库插入用户注册的信息
                        g.db.execute('insert into userinfo (username, password) values (?, ?)', [
                            request.form['username'], request.form['password']])
                        g.db.commit()
                        # 会乱码，解码为utf-8
                        msg = '注册成功'.decode('utf-8')
                        url = 'show_entries'
                    else:
                        # 会乱码，解码为utf-8
                        msg = '账号已被注册'.decode('utf-8')
                        url = 'login'

                    flash(msg)
                    return redirect(url_for(url))
                msg = '请输入4~16位字符!'.decode('utf-8')
                flash(msg)
                return redirect(url_for('login'))

        msg = '不允许使用除字母数字下划线之外的字符!'.decode('utf-8')
        flash(msg)
        return redirect(url_for('register'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    '''退出登录'''
    session.pop('logged_in', None)
    app.config['USERNAME'] = ''
    app.config['UID'] = ''
    msg = '已经退出！'.decode('utf-8')
    flash(msg)
    return redirect(url_for('show_entries'))


if __name__ == "__main__":
    # 生成数据库
    if 'flaskr.db' not in os.listdir('./'):
        init_db()
    # app.run(host='0.0.0.0')
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
