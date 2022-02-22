from django.shortcuts import render, HttpResponse, redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from pymongo import MongoClient
from email import message
from email.policy import HTTP
from lib2to3.pgen2.tokenize import generate_tokens
import re
import datetime
import pytz
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode 
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode
from neo4j import GraphDatabase
import pandas
import numpy
from jira import JIRA


# Create your views here.
def index(request):
    context = {
        "variable1":"Knowledge Platform is great",
        "variable2":"CDATA is great"
    } 
    return render(request, "authentication/index.html", context)

def about(request):
    return render(request, 'authentication/about.html') 

def signup(request):
    
    if request.method == "POST":
        # global username 
        username = request.POST.get('username')
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')
            
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
            
            
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')
        
     
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        
        messages.success(request, " We have sent account activation link to your registered mail id. Kindly click on the link to activate your account .")
        
        
        #welcome email
        
        subject = "Welcome to Knowledge Platform - Django Login!!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to Knowledge Platform!! \n Thank You for visiting our website \n We have also sent you a confirmation email, Please confirm your email address in order to activate yor account. \n\n Thanking You\n Smriti Misra"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        
        #Email Address confirmation email
        
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Knowledge Platform - Django Login"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
    
    return render(request, "authentication/signup.html")

def contribute(request):
    if request.method == "POST":
        ptype=request.POST['ptype']
        psummary=request.POST['psummary']
        pdescription=request.POST['pdescription']
        products=request.POST.getlist('CD')
        kanalysis=request.POST['kanalysis']
        kinsisghts=request.POST['kinsisghts']
        tags=request.POST['tags']
        owner=request.POST['owner']     
        datetime_entry = datetime.datetime.now() 
        # username = request.session.get('username') 
        conn = MongoClient()
        db=conn.Lucid
        collection=db.knowledge
        # username=signup.username
        
        # # if datetime_logout1 is None:
        #     datetime_logout1=0  
        rec1={
          "username":username1,          
          "ptype":ptype,
          "psummary":psummary,
          "pdescription":pdescription,
          "products":products,
          "kanalysis":kanalysis,
          "kinsisghts":kinsisghts,
          "tags":tags,
          "owner":owner,
          "date_of_entry":datetime_entry.strftime('%Y/%m/%d %I:%M:%S:%p'),
          "date_of_login":datetime_login1.strftime('%Y/%m/%d %I:%M:%S:%p'),
        #   "date_of_logout":datetime_logout1
        }
        collection.insert_one(rec1)

        # added neo4j database
        #neo4j_create_statemenet = "create (a: Problem{name:'%s'}), (k:Owner {owner:'%s'}), (l:Problem_Type{type:'%s'}),(m:Problem_Summary{summary:'%s'}), (n:Probelm_Description{description:'%s'}),(o:Knowledge_Analysis{analysis:'%s'}), (p:Knowledge_Insights{kinsisghts:'%s'}), (a)-[:Owner]->(k), (a)-[:Problem_Type]->(l), (a)-[:Problem_Summary]->(m), (a)-[:Problem_Description]->(n), (a)-[:Knowledge_analysis]->(o), (a)-[:Knowledge_insights]->(p)"%("Problem",owner,type,summary,description,analysis,insights)
        graphdb=GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "admin"))
        session=graphdb.session()
        q2='''Merge (a:Owner {owner:'%s'})
        Merge (b:Problem_Type{ptype:'%s'}) 
        Merge(c:Problem_Summary{psummary:'%s'})
        Merge (d:Problem_Description{pdescription:'%s'})
        Merge (e:Knowledge_Analysis{kanalysis:'%s'})
        Merge(f:Knowledge_Insights{kinsisghts:'%s'})
        Merge (g:Tag{tag:'%s'})
        Merge (h:Product{product:'%s'})
        MERGE (b)-[:OWNER]->(a)
        MERGE (b)-[:PROBLEM_SUMMARY]->(c)
        MERGE (b)-[:PROBLEM_DESCRIPTION]->(d)
        MERGE (b)-[:KNOWLEDGE_ANALYSIS]->(e)
        MERGE (b)-[:KNOWLEDGE_INSIGHTS]->(f)
        MERGE (b)-[:TAG]->(g)
        MERGE (b)-[:PRODUCT]->(h)'''%(owner,ptype,psummary,pdescription,kanalysis,kinsisghts,tags,*products)
        q1=" match(n) return n "
    
        session.run(q2)
        session.run(q1)

        messages.success(request, 'Your message has been sent!')
    return render(request, 'authentication/contribute.html')


def defects(request):
    conn = MongoClient()
    db=conn.Lucid
    collection=db.knowledge
    defectdata =collection.find({'ptype':'defect'})
    return render(request, 'knowledgepages/defects.html', {'defectdata': defectdata.clone()}) 

    
def index(request):
    print(request.user)
    return render(request, "authentication/index.html")

def signin(request):  
     
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
    #below we are doing user authentication  
      
        user = authenticate(username=username, password=pass1)   
         
        if user is not None:
             login(request, user)
             fname = user.first_name
             current_user = {}
             global username1
             username1=username
             datetime_login = datetime.datetime.now()
             global datetime_login1
             datetime_login1=datetime_login
             return render(request, "authentication/index.html", {'fname': fname})
             
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')
    
    
    return render(request, "authentication/signin.html")



def signout(request):
    logout(request)
    datetime_logout = datetime.datetime.now()
    global datetime_logout1
    datetime_logout1=datetime_logout
    messages.success(request, "Logged Out Successfully")
    return redirect('home')

def activate(request, uidb64, token):
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def jira(request):
    jiraid=request.POST.get('jiraid')
    # print(jiraid)
    pname=str(request.POST.get('pname'))
    #print(pname)
    
    #serv="https://"+pname+".atlassian.net/"
    #print(serv)

    gm=str(request.POST.get('email'))
    print(gm)
    
    tok=str(request.POST.get('token'))
    print(tok)


    jiraOptions = {'server': "https://knowledgeplatform.atlassian.net/"}
    #jiraOptions = {'server': serv}

    jira = JIRA(options=jiraOptions, basic_auth=("mangalyogesh.22@gmail.com", "B8DrrneqVJcOGbyzHJ8jDC9F"))
    #creds of shashank: "shashankshukla137@gmail.com", "R71mWwO95pvcFo48tnpG9F8A"
    #jira = JIRA(options=jiraOptions, basic_auth=(gm, tok))
    
    for singleIssue in jira.search_issues(jql_str='project = knowledgeplatform'):
        print('{}: {}:{}'.format(singleIssue.key, singleIssue.fields.summary,singleIssue.fields.reporter.displayName))
    for singleIssue in jira.search_issues(jql_str='project = knowledgeplatform'):
        if(singleIssue.key==jiraid):
            print("Field Summary is",singleIssue.fields.summary)
            print("Reporter Name is",singleIssue.fields.reporter.displayName)
            break
    else:
        print("Jira Id is Invalid")

    global d
    d={'key':[],'summary':[],'name':[]}
    for singleIssue in jira.search_issues(jql_str='project = knowledgeplatform'):
        d['key'].append(singleIssue.key)
        d['summary'].append(singleIssue.fields.summary)
        d['name'].append(singleIssue.fields.reporter.displayName)    
    print(d,type(d))

    return render(request,'knowledgepages/jira.html')


def jiradisplay(request):
    return render(request,'knowledgepages/jiradisplay.html',d)