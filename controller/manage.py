# coding: utf-8
from pony.orm import *
from .base import BaseHandler
from tornado.web import *
from model import *
import time
import datetime
import random,string,shutil

# __author__ = 'hfli'

# class VendorManageHandler(BaseHandler):
# 	def get(self):
# 		self.write("This is Vendor Manage dashboard")

def format_date(date):
#TODO:
#        date = time.localtime(date)
        return datetime.datetime.utcfromtimestamp(date).strftime("%Y-%m-%d:%H:%M:%S")

class RegisterHandler(BaseHandler):
	def get(self):
		self.render("register.html")
	@db_session
	def post(self):
                print(self.request.arguments)
		alias=self.get_argument("nickname")
                password=self.get_argument("passwd")
                email=self.get_argument("email")
                if(password!="" and email!="" and alias!=""):
                    User(alias=alias,passwd=password,email=email)
                self.redirect("/")

class IndexHandler(BaseHandler):
	@db_session
	def get(self):
            posts = select(p for p in Post).order_by(Post.created_date.desc())
            self.render("index.html",posts=posts, format_date=format_date, user=self.current_user)
	def post(self):
		pass
	def edit(self):
		pass
	def remove(self):
		pass
class EditHandler(BaseHandler):
    @db_session
    def get(self):
        kind=self.get_argument("kind")
        postid=self.get_argument("id")
        if(kind == "subpost"):
            pass
        elif (kind == "post"):
            pass

class DelHandler(BaseHandler):
    @db_session
    def get(self):
        kind=self.get_argument("kind")
        postid=self.get_argument("id")
        if(kind == "subpost"):
            post=SubPost.get(id=postid)
            if(post!=None):
                post.delete() 
            
        elif kind == "post":
            post=Post.get(id=postid)
            if(post!=None):
		path="static/"+str(post.id)
		if os.path.exists(path):
		    shutil.rmtree(path)
                post.delete()

        self.redirect(self.request.headers['referer'])

class PostHandler(BaseHandler):
    @db_session
    @authenticated
    def get(self):
        post_id = self.get_argument("id")
        post = get(p for p in Post if p.id == post_id)
        if os.path.exists("static/"+str(post.id)):
	        files=os.listdir("static/"+str(post.id))
	        for index in range(len(files)):
		        files[index]="static/"+str(post.id)+"/"+files[index]
	else :
	        files=[]
        subpost = select(p for p in SubPost if p.post == post).order_by(SubPost.created_date.desc())
        self.render("post.html",post=post,subposts=subpost,format_date=format_date,files=files)

    @db_session
    def post(self, *args, **kwargs):
        if( not self.is_login()):
            self.redirect("/login")
        title=self.get_argument("submit_title")
        content=self.get_argument("submit_post_content")
        author=User.get(alias=self.current_user)
        created_date=int(time.time())
        post=Post(title=title,content=content,user=author,created_date=created_date,updated_date=created_date)
        commit()
        if self.request.files:
            uploadfile=self.request.files['inputfile'][0]
	    print(uploadfile)
            filename='static/'+str(post.id)
            if not os.path.exists(filename):
	            os.mkdir(filename)
	    fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(60))
	    extension=os.path.splitext(uploadfile['filename'])[1]
            filename +='/'+fname+extension
            uploadfile_handle=open(filename,'wb')
            uploadfile_handle.write(uploadfile['body'])
        self.redirect("/")


class AddSubPostHandler(BaseHandler):
    @db_session
    def post(self):
        if( not self.is_login()):
            self.redirect("/login")
        post_id = self.get_argument("post_id")
        title=self.get_argument("submit_title")
        content=self.get_argument("submit_post_content")
        author=User.get(alias=self.current_user)
        created_date=int(time.time())
        post = get(p for p in Post if p.id==post_id)
        if(post != None):
            SubPost(title=title,user=author,post=post,content=content,created_date=created_date)
        else:
            self.write("滚")
            return
        self.redirect("/post_content?id=%s"% (post_id))
#        subposts = select (p for p in SubPost if p.post==post)
class LoginHandler(BaseHandler):
    loginerror = None
    def get(self):
	self.render("login.html",error=self.loginerror)
    @db_session
    def post(self):
        alias=self.get_argument("nickname")
        password=self.get_argument("password")
        user=get(p for p in User if p.alias == alias and p.passwd==password)
        print(user)
	if(user !=None):
            self.write("登录成功")
            self.set_secure_cookie("user",alias)
            self.redirect("/")
        else:
            self.loginerror="用户名，密码错误"
            self.render("login.html",error=self.loginerror)

class LogoutHandler(BaseHandler):
    def get(self):
        if(self.current_user!=""):
            self.clear_cookie("user")
            self.redirect("/")
	
    def post(self):
	pass
