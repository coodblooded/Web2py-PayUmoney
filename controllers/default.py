# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

import datetime
import hashlib
from random import randint

def index():
    MERCHANT_KEY = "xxxxxx"
    key="xxxxxx"
    SALT = "********"
    PAYU_BASE_URL = "https://secure.payu.in/_payment"
    action = ''
    posted = {}
    posted['email'] = 'patelsandeep126@gmail.com'
    posted['firstname'] = 'Sandeep Patel'
    posted['productinfo'] = 'payment'
    posted['amount'] = '1200.0'
    posted['furl'] = 'http://{}/{}/{}/failure.html'.format(request.env.http_host,request.application,request.controller)
    posted['surl'] = 'http://{}{}/{}/success.html'.format(request.env.http_host,request.application,request.controller)
    posted['service_provider'] = 'payu_paisa'
    posted['phone'] = '7580979169'
    for i in request.post_vars:
        posted[i]=request.vars[i]
    hash_object = hashlib.sha256(b'randint(0,20)')
    txnid=hash_object.hexdigest()[0:20] 
    hashh = ''
    posted['txnid']=txnid
    hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
    posted['key']=key
    hash_string=''
    hashVarsSeq=hashSequence.split('|')
    for i in hashVarsSeq:
        try:
            hash_string+=str(posted[i])
        except Exception:
            hash_string+=''
        hash_string+='|'
    hash_string+=SALT
    posted['hash_string'] = hash_string
    hashh=hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
    posted['hash'] = hashh
    posted['posted'] = str({'txnid' : txnid,'key':key})
    action =PAYU_BASE_URL
    if(posted.get("key")!=None and posted.get("txnid")!=None and posted.get("productinfo")!=None and posted.get("firstname")!=None and posted.get("email")!=None):
        return dict(posted = posted,hashh=hashh,MERCHANT_KEY=MERCHANT_KEY,txnid=txnid,hash_string=hash_string,action="https://secure.payu.in/_payment")
    else:
        return dict(posted = posted,hashh=hashh,MERCHANT_KEY=MERCHANT_KEY,txnid=txnid,hash_string=hash_string,action="")

    return locals()


def success():
    c = {}
    c.update(request.vars)
    status=request.vars["status"]
    firstname=request.post_vars["firstname"]
    amount=request.post_vars["amount"]
    txnid=request.post_vars["txnid"]
    posted_hash=request.post_vars["hash"]
    key=request.post_vars["key"]
    productinfo=request.post_vars["productinfo"]
    email=request.post_vars["email"]
    salt="4mkcJFKuBQ"
    try:
        additionalCharges=request.post_vars["additionalCharges"]
        retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
    except Exception:
        retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
    hashh=hashlib.sha512(retHashSeq.encode('utf-8')).hexdigest().lower()
    if(hashh !=posted_hash):
        print ("Invalid Transaction. Please try again")
    else:
        print ("Thank You. Your order status is ", status)
        print ("Your Transaction ID for this transaction is ",txnid)
        print ("We have received a payment of Rs. ", amount ,". Your order will soon be shipped.")
    return dict(txnid=txnid,status=status,amount=amount)



def failure():
    c = {}
    c.update(request.vars)
    status=request.post_vars["status"]
    firstname=request.post_vars["firstname"]
    amount=request.post_vars["amount"]
    txnid=request.post_vars["txnid"]
    posted_hash=request.post_vars["hash"]
    key=request.post_vars["key"]
    productinfo=request.post_vars["productinfo"]
    email=request.post_vars["email"]
    salt="4mkcJFKuBQ"
    try:
        additionalCharges=request.post_vars["additionalCharges"]
        retHashSeq=additionalCharges+'|'+salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
    except Exception:
        retHashSeq = salt+'|'+status+'|||||||||||'+email+'|'+firstname+'|'+productinfo+'|'+amount+'|'+txnid+'|'+key
        hashh=hashlib.sha512(retHashSeq.encode('utf-8')).hexdigest().lower()
        print ("Thank You. Your order status is ", status)
        print ("Your Transaction ID for this transaction is ",txnid)
        print ("We have received a payment of Rs. ", amount ,". Your order will soon be shipped.")
    return locals()
