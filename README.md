# Flask-Demo

调用一次init_db()函数，用于生成sqlite3数据库。
ps：现在不需要了，直接运行flaskr.py即可

## 虚拟环境配置

Python版本：
```
Python2.7
```

安装
```shell
sudo pip install virtualenv
sudo pip install virtualenvwrapper

```
在`/home/xxx/`目录下的`.bashrc`文件中添加：
```shell
export WORKON_HOME=~/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
```

保存退出并执行`source .bashrc`。



## 安装flask
进入虚拟环境目录`~/.virtualenvs`，使用`virtualenv  虚拟环境名称`创建虚拟环境。

还可以使用`virtualenv -p 虚拟环境版本(如/usr/bin/python3) 虚拟环境名称`创建指定Python版本的虚拟环境。

`workon 虚拟环境名称`进入虚拟环境，在任何目录下都可以执行。

在虚拟环境中安装模块时，不需要使用`sudo`，如果使用`sudo`会把模块安装在系统中的`Python`中。

```Python
pip install flask
```
