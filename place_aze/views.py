from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages, sessions
from django.views.decorators.csrf import csrf_exempt
from .models import Student,Admin,Teacher,Questions,Test,StudentProfile,Subscribe,StudentResults,StudentAns
import razorpay
from django.conf import settings
import math,random
from .mails import studentVerificationOTP, adminVerificationOTP, teacherVerificationOTP,teacherAccept, teacherReject, ForgotPasswordOTP
from .functions import handle_uploaded_file,handle_uploaded_student_file
from coolname import generate_slug
import pandas as pd
import numpy as np
import datetime
from django.http import HttpResponseBadRequest

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
 
# @csrf_exempt
#OTP Generator
def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(5) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP

@csrf_exempt
#Landing Page
def home(request):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            return redirect("/adminDashboard/")
        except:
            try:
                tUser=Teacher.objects.get(tUser=request.user)
                return redirect("/teacherDashboard/")
            except:
                sObj=Student.objects.get(stUser=request.user)
                obj=Subscribe.objects.filter(stid=sObj.stid)
                data={}
                if obj:
                    found=0
                    sUid=0
                    date=0
                    for i in obj:
                        subscribeDate=i.subscribeDate
                        given_date = datetime.datetime.fromtimestamp(subscribeDate.timestamp())
                        current_date = datetime.datetime.now()
                        difference_in_days = (current_date - given_date).days
                        if difference_in_days<180:
                            found=1
                            sUid=i.sUid
                            date=subscribeDate
                    if found==1:
                        timestamp=datetime.datetime.fromtimestamp(subscribeDate.timestamp())
                        # timestamp = datetime.datetime.strptime(subscribeDate.timestamp(), '%Y-%m-%d %H:%M:%S')
                        remaining_time = datetime.datetime.now()-timestamp
                        data["remainingTime"]=180-remaining_time.days
                return render(request,'index.html',data)
            
    return render(request,'index.html')

@csrf_exempt
#Student Login Page Call
def studentLoginPage(request):
    return render(request,'studentLoginPage.html')

@csrf_exempt
#Student SignUp Page Call
def studentSignupPage(request):
    return render(request,'studentSignupPage.html')

@csrf_exempt
#Student Signup OTP
def studentSignupOTP(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    try:
        usname=User.objects.get(username=email)
        messages.error(request, email + ' already exist !!!')
        return redirect("/studentLoginPage/")
    except: 
        otp=generateOTP()
        studentVerificationOTP(email,otp)
        # request.session['stemail']=email
        # request.session['otp']=otp
        # request.session['password']=password
        # request.session['otp_given']=True
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
        expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        request.session["details"]={'stemail':email,"otp":otp,"password":password,'expiryTime':expiryTime}
        messages.success(request, 'Please check your mail for OTP ')
        # print(request.session['stemail'])
    return redirect("/studentSignupPage/")

@csrf_exempt
#Student Signup
def studentSignup(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    sotp=details["otp"]
    if(eotp==sotp):
        user = User.objects.create_user(username=details['stemail'],password=details['password'])
        user.is_active=True
        user.save()
        obj=Student.objects.create(stUser=user,email=details['stemail'])
        del request.session["details"]
        messages.success(request, 'Registered Successfully !!!')
        return redirect("/studentLoginPage/")
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/studentSignupPage")

@csrf_exempt
#Student Login
def studentLogin(request): 
    email=request.POST.get("email")
    pwd=request.POST.get("password")
    try:
        user = User.objects.get(username=email)
        stUser=Student.objects.get(stUser=user)
        if stUser is not None:
            user= authenticate(request,username=email,password=pwd)
            if user is not None:
                login(request,user)
                return redirect("/")
            else:
                messages.error(request,"Password is incorrect")
                return redirect("/studentLoginPage/")
        else:
            messages.error(request,email+" not found!!!")
            return redirect("/studentLoginPage/")
    except:
        messages.error(request,email+" not found!!!")
        return redirect("/studentLoginPage/")
    
@csrf_exempt
#Logout
def logoutUser(request):
    logout(request)
    return redirect("/")

@csrf_exempt
#Admin Login Page Call
def adminLoginPage(request):
    return render(request,"adminLoginPage.html")

@csrf_exempt
#Admin Login OTP
def adminLoginOTP(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    try:
        # usname=User.objects.get(username=email)
        aObj=Admin.objects.get(email=email)
        if aObj is None:
            messages.error(request, email +" you don't have an Admin Access !!!")
            return redirect("/adminLoginPage/")
        # otp=generateOTP()
        otp="12345"
        adminVerificationOTP(email,otp)
        # request.session['ademail']=email
        # request.session['otp']=otp
        # request.session['password']=password
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
        expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        request.session['details']={'ademail':email,'otp':otp,'password':password,'expiryTime':expiryTime}
        messages.success(request, 'Please check your mail for OTP ')
    except:
        messages.error(request, email +" you don't have an Admin Access !!!")
        return redirect("/adminLoginPage/")
        
    return redirect("/adminLoginPage/")

@csrf_exempt
#Admin Login
def adminLogin(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    # print(details['otp'])
    # print(details)
    sotp=details["otp"]
    if(eotp==sotp):
        # user= authenticate(request,username=request.session['ademail'],password=request.session['password'])
        user= authenticate(request,username=details['ademail'],password=details['password'])
        # request.session.clear()
        del request.session["details"]
        if user is not None:
            login(request,user)
            return redirect("/adminDashboard/")
        else:
            messages.error(request,"Password is incorrect")
            return redirect("/adminLoginPage/")
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/adminLoginPage/")

@csrf_exempt
#Admin Dashboard
def adminDashboard(request):
    if request.user.is_authenticated:
        try:
            obj=Admin.objects.get(adUser=request.user)
            return render(request,'adminDashboard.html')
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Approve Teacher Page
def approveTeacherPage(request):
    if request.user.is_authenticated:
        try:
            obj=Admin.objects.get(adUser=request.user)
            a=User.objects.filter(is_active=False)
            inactiveTeachers=[]
            for i in a:
                j=Teacher.objects.get(email=i.username)
                inactiveTeachers.append([j.fname+" "+j.lname,j.email,j.tid])
            data={'inactiveTeachers':inactiveTeachers}
            return render(request,'approveTeacherPage.html',data)
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Approve Quiz Page
def approveQuizPage(request):
    if request.user.is_authenticated:
        try:
            obj=Admin.objects.get(adUser=request.user)
            tObj=Test.objects.filter(approved=0)
            inactiveTest=[]
            for i in tObj:
                inactiveTest.append([i.tUid,i.email,i.testId,i.subject])
            print(inactiveTest)
            return render(request,'approveQuizPage.html',{"inactiveTest":inactiveTest})
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Teacher Dashboard
def teacherDashboard(request):
    if request.user.is_authenticated:
        try:
            obj=Teacher.objects.get(tUser=request.user)
            return render(request,'teacherDashboard.html',{'name':obj.fname+" "+obj.lname,"pic":obj.picture})
        except:
            try:
                obj=Admin.objects.get(adUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/adminDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/teacherLoginPage/')
    
@csrf_exempt
#Teacher Login Page
def teacherLoginPage(request):
    return render(request,'teacherLoginPage.html')

@csrf_exempt
#Teacher Signup Page call
def teacherSignupPage(request):
    return render(request,"teacherSignupPage.html")

@csrf_exempt
#Teacher Signup OTP
def teacherSignupOTP(request):
    firstName = request.POST.get("firstName")
    lastName = request.POST.get("lastName")
    mobile = request.POST.get("mobile")
    course = request.POST.get("course")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")
    img = request.FILES.get("img")
    try:
        usname=User.objects.get(username=email)
        messages.error(request, email + ' already exist !!!')
        return redirect("/teacherLoginPage/")
    except: 
        otp=generateOTP()
        teacherVerificationOTP(email,otp)
        # request.session['firstName']=firstName
        # request.session['lastName']=lastName
        # request.session['mobile']=mobile
        # request.session['course']=course
        # request.session['email']=email
        # request.session['password']=password
        # request.session['address']=address
        # request.session['otp']=otp
        # request.session['imgName']=img.name
        handle_uploaded_file(img)
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
        expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        request.session["details"]={"firstName":firstName,"lastName":lastName,"mobile":mobile,"course":course,"email":email,"password":password,"address":address,"otp":otp,"imgName":img.name,'expiryTime':expiryTime}
        messages.success(request, 'Please check your mail for OTP ')
    return redirect("/teacherSignupPage/")

@csrf_exempt
#Teacher Signup
def teacherSignup(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    sotp=details["otp"]
    if(eotp==sotp):
        user = User.objects.create_user(username=details['email'],password=details['password'])
        user.is_active=False
        user.save()
        obj=Teacher.objects.create(tUser=user,email=details["email"],fname=details["firstName"],lname=details["lastName"],mob=details["mobile"],course=details["course"],address=details["address"],picture='teacherPics/'+details['imgName'])
        del request.session["details"]
        messages.success(request, 'Registered Successfully !!!')
        return redirect("/teacherLoginPage/")
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/teacherSignupPage")

@csrf_exempt
#Teacher Login
def teacherLogin(request): 
    email=request.POST.get("email")
    pwd=request.POST.get("password")
    try:
        user = User.objects.get(username=email)
        tUser=Teacher.objects.get(tUser=user)
        if tUser is not None:
            if (user.is_active==False):
                messages.error(request,tUser.email+" you aren't approved by admin")
                return redirect("/teacherLoginPage/")
            user= authenticate(request,username=email,password=pwd)
            if user is not None:
                login(request,user)
                return redirect("/teacherDashboard/")
            else:
                messages.error(request,"Password is incorrect")
                return redirect("/teacherLoginPage/")
        else:
            messages.error(request,email+" not found!!!")
            return redirect("/teacherLoginPage/")
    except:
        messages.error(request,email+" not found!!!")
        return redirect("/teacherLoginPage/")

@csrf_exempt
#View Teacher Details
def displayTeacherDetails(request,tid):
    if request.user.is_authenticated:
        try:
            user=Admin.objects.get(adUser=request.user)
            obj=Teacher.objects.get(tid=tid)
            data={'tid':tid,'email':obj.email,'fname':obj.fname,'lname':obj.lname,'mob':obj.mob,'course':obj.course,'address':obj.address,'pic':obj.picture}
            return render(request,'viewTeacherDetails.html',data)
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Accept Teacher
def acceptTeacher(request,tid):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            obj=Teacher.objects.get(tid=tid)
            tUser=User.objects.get(username=obj.email)
            tUser.is_active=True
            tUser.save()
            teacherAccept(obj.email)
            messages.success(request,obj.email+ "has been accepted")
            return redirect("/approveTeacherPage/")
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Reject Teacher
def rejectTeacher(request,tid):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            obj=Teacher.objects.get(tid=tid)
            tUser=User.objects.get(username=obj.email)
            teacherReject(obj.email)
            messages.success(request,obj.email+ "has been rejected")
            tUser.delete()
            return redirect("/approveTeacherPage/")
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt
#Create Test Page
def createTestPage(request):
    if request.user.is_authenticated:
        try:
            obj=Teacher.objects.get(tUser=request.user)
            return render(request,'createTestPage.html')
        except:
            try:
                obj=Admin.objects.get(adUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/adminDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/teacherLoginPage/') 

@csrf_exempt 
#Create Test
def createTest(request):
    obj=Teacher.objects.get(tUser=request.user)
    teacherID=obj.tid
    startDate = request.POST.get("startDate")
    endDate = request.POST.get("endDate")
    startTime = request.POST.get("startTime")
    endTime = request.POST.get("endTime")
    startDateTime = str(startDate) + " " + str(startTime)
    endDateTime = str(endDate) + " " + str(endTime)
    duration = int(request.POST.get("duration"))
    subject = request.POST.get("subject")
    topic = request.POST.get("topic")
    doc = request.FILES.get("doc")
    testId = generate_slug(2)
    ef = pd.read_csv(doc)
    fields = ['qid','q','a','b','c','d','ans','marks']
    df = pd.DataFrame(ef, columns = fields)
    # print(df)
    for row in df.index:
        a=Questions.objects.create(testId=testId,qId=df['qid'][row],q=df['q'][row],a=df['a'][row],b=df['b'][row],c=df['c'][row],d=df['d'][row],ans=df['ans'][row],marks=df['marks'][row],teacherId=teacherID)
    
    a=Test.objects.create(email=obj.email,testId=testId,start=startDateTime,end=endDateTime,duration=duration,subject=subject,topic=topic,teacherId=teacherID,approved=0)
    messages.success(request,"Test created successfully")
    return redirect ('/teacherDashboard/')

@csrf_exempt
#View Tests Page
def viewTestPage(request):
    obj=Teacher.objects.get(tUser=request.user)
    test=Test.objects.filter(teacherId=obj.tid)
    testDetails=[]
    for i in test:
        testDetails.append([i.testId,i.subject,i.topic])
    data={'testDetails':testDetails}
    return render(request,"viewTestPage.html",data)

@csrf_exempt
#View All Quizzes
def viewAllQuizzes(request):
    test=Test.objects.filter(approved=1)
    testDetails=[]
    for i in test:
        testDetails.append([i.testId,i.subject,i.topic,i.email,i.start.date(),i.start.time(),i.end.date(),i.end.time()])
    data={'testDetails':testDetails}
    return render(request,"viewAllQuizzes.html",data)

@csrf_exempt
#Display Questions Page
def displayQuestionsPage(request,testId): 
    obj=Questions.objects.filter(testId=testId)
    qList=[]
    for i in obj:
        qList.append([i.qId,i.q,i.a,i.b,i.c,i.d,i.ans,i.marks,i.qUid])
    return render(request,'displayQuestionsPage.html',{'qList':qList})

@csrf_exempt
#Display Quiz
def displayQuiz(request,testId): 
    obj=Questions.objects.filter(testId=testId)
    qList=[]
    for i in obj:
        qList.append([i.qId,i.q,i.a,i.b,i.c,i.d,i.ans,i.marks,i.qUid])
    return render(request,'displayQuiz.html',{'qList':qList})

@csrf_exempt
#View Quiz Page
def viewQuizPage(request,testId): 
    obj=Questions.objects.filter(testId=testId)
    tObj=Test.objects.get(testId=testId)
    qList=[]
    for i in obj:
        qList.append([i.qId,i.q,i.a,i.b,i.c,i.d,i.ans,i.marks])
    return render(request,'viewQuizPage.html',{'qList':qList,'testId':testId,'startDate':tObj.start.date(),'startTime':tObj.start.time(),'endDate':tObj.end.date(),'endTime':tObj.end.time(),'duration':tObj.duration,'subject':tObj.subject,'topic':tObj.topic})

@csrf_exempt
#Quiz Page
def studentQuizPage(request):
    if request.user.is_authenticated:
        currentTime=datetime.datetime.now()
        sObj=Student.objects.get(stUser=request.user)
        subObj=Subscribe.objects.filter(stid=sObj.stid)
        if not subObj:
            messages.error(request,"Subscribe First to view Quizzes")
            return redirect("/")
        else:
            found=0
            for i in subObj:
                given_date = datetime.datetime.fromtimestamp(i.subscribeDate.timestamp())
                # Get current date
                current_date = datetime.datetime.now()
                # Calculate the difference in days
                difference_in_days = (current_date - given_date).days
                if difference_in_days<180:
                    found=1
            if found==0:
                messages.error(request,"Subscribe First to view Quizzes")
                return redirect("/")
            else:
                obj=Test.objects.all()
                liveQuizzes=[]
                upcomingQuizzes=[]
                endedQuizzes=[]
                current=datetime.datetime.now()
                
                for i in obj:
                    if(i.approved==0):
                        continue 
                    if(current.timestamp()>=i.start.timestamp() and current.timestamp()<=i.end.timestamp() ):
                        liveQuizzes.append([i.testId,i.start.time(),i.end.time(),i.duration,i.subject,i.topic,i.start.date(),i.end.date()])
                    elif(current.timestamp()<i.start.timestamp()):
                        upcomingQuizzes.append([i.testId,i.start.time(),i.end.time(),i.duration,i.subject,i.topic,i.start.date(),i.end.date()])
                    else:
                        endedQuizzes.append([i.testId,i.start.time(),i.end.time(),i.duration,i.subject,i.topic,i.start.date(),i.end.date()])
                return render(request,"studentQuizPage.html",{'upcomingQuizzes':upcomingQuizzes,'liveQuizzes':liveQuizzes,'endedQuizzes':endedQuizzes})
    else:
        messages.error(request,"Login First !!!")
        return redirect("/")

@csrf_exempt
#Give Test
def giveTest(request,testId):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            messages.error(request,"You don't have access")
            return redirect("/adminDashboard/")
        except:
            try:
                tUser=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access")
                return redirect("/teacherDashboard/")
            except:
                tobj=Test.objects.get(testId=testId)
                currentTime=datetime.datetime.now()
                if(currentTime.timestamp()>tobj.end.timestamp()):
                    messages.error(request,"Test has been expired")
                    return redirect("/studentQuizPage/")
                obj=Questions.objects.filter(testId=testId)
                qList=[]
                for i in obj:
                    qList.append([i.qUid,i.qId,i.q,i.a,i.b,i.c,i.d,i.marks])
                data={'qList':qList,'subject':tobj.subject,'topic':tobj.topic,'duration':tobj.duration,'testId':testId}
                return render(request,'giveTest.html',data)
    messages.error(request,"You should login first to appear for the tests.")      
    return redirect("/studentQuizPage/")

@csrf_exempt
#View Test
def viewTest(request,testId):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            messages.error(request,"You don't have access")
            return redirect("/adminDashboard/")
        except:
            try:
                tUser=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access")
                return redirect("/teacherDashboard/")
            except:
                tobj=Test.objects.get(testId=testId)
                currentTime=datetime.datetime.now()
                obj=Questions.objects.filter(testId=testId)
                qList=[]
                for i in obj:
                    qList.append([i.qUid,i.qId,i.q,i.a,i.b,i.c,i.d,i.marks,i.ans])
                data={'qList':qList,'subject':tobj.subject,'topic':tobj.topic,'duration':tobj.duration,'testId':testId}
                return render(request,'viewTest.html',data)
    messages.error(request,"You should login first to appear for the tests.")      
    return redirect("/studentQuizPage/")

@csrf_exempt
#Submit Test
def submitTest(request,testId):
    qObj=Questions.objects.filter(testId=testId)
    sObj=Student.objects.get(stUser=request.user)
    stId=sObj.stid
    scoredMarks=0
    testGivenId=generate_slug()
    for i in qObj:
        markedAns=request.POST.get(str(i.qUid))
        ans=i.ans
        marks=i.marks
        if markedAns==ans:
            scoredMarks+=marks
        if markedAns!=None:
            saObj=StudentAns.objects.create(qUid=i.qUid,testId=testId,stid=stId,markedAns=markedAns,ans=ans,marks=marks,testGivenId=testGivenId)
        else: 
            saObj=StudentAns.objects.create(qUid=i.qUid,testId=testId,stid=stId,markedAns="",ans=ans,marks=marks,testGivenId=testGivenId)
    srObj=StudentResults.objects.create(stid=stId,testId=testId,scoredMarks=scoredMarks,submitDate=datetime.datetime.now(),testGivenId=testGivenId)
    messages.success(request,"Test submitted successfully")
    return redirect("/studentQuizPage/")

@csrf_exempt
#Student Result Page
def studentResultPage(request):
    stObj=Student.objects.get(email=request.user)
    srObj=StudentResults.objects.filter(stid=stObj.stid)
    subObj=Subscribe.objects.filter(stid=stObj.stid)
    if not subObj:
        messages.error(request,"Subscribe First to view Results")
        return redirect("/")
    else:
        found=0
        for i in subObj:
            given_date = datetime.datetime.fromtimestamp(i.subscribeDate.timestamp())
            # Get current date
            current_date = datetime.datetime.now()
            # Calculate the difference in days
            difference_in_days = (current_date - given_date).days
            if difference_in_days<180:
                found=1
        if found==0:
            messages.error(request,"Subscribe First to View Results")
            return redirect("/")
        else:
            resultList=[]
            for i in srObj:
                testId=i.testId
                scoredMarks=i.scoredMarks
                submitDate=i.submitDate.date()
                testGivenId=i.testGivenId
                tObj=Test.objects.get(testId=testId)
                subject=tObj.subject
                resultList.append([testId,scoredMarks,submitDate,subject,testGivenId])
            return render(request,"studentResultPage.html",{'resultList':resultList,'stId':stObj.stid})

@csrf_exempt
#View Answers
def viewAnswers(request,stId,testId,testGivenId):
    saObj=StudentAns.objects.filter(testId=testId,stid=stId,testGivenId=testGivenId)
    qList=[]
    for i in saObj:
        obj=Questions.objects.get(qUid=i.qUid)
        qList.append([obj.qId,obj.q,obj.a,obj.b,obj.c,obj.d,obj.ans,obj.marks,i.markedAns])
    return render(request,'viewAnswersPage.html',{'qList':qList})

@csrf_exempt
#Display Answers
def displayAnswers(request,stId,testId,testGivenId):
    saObj=StudentAns.objects.filter(testId=testId,stid=stId,testGivenId=testGivenId)
    qList=[]
    for i in saObj:
        obj=Questions.objects.get(qUid=i.qUid)
        qList.append([obj.qId,obj.q,obj.a,obj.b,obj.c,obj.d,obj.ans,obj.marks,i.markedAns])
    return render(request,'displayAnswersPage.html',{'qList':qList})

@csrf_exempt
#Display Solutions
def displaySolutions(request,stId,testId,testGivenId):
    saObj=StudentAns.objects.filter(testId=testId,stid=stId,testGivenId=testGivenId)
    qList=[]
    for i in saObj:
        obj=Questions.objects.get(qUid=i.qUid)
        qList.append([obj.qId,obj.q,obj.a,obj.b,obj.c,obj.d,obj.ans,obj.marks,i.markedAns])
    return render(request,'displaySolutionsPage.html',{'qList':qList})

@csrf_exempt
#Result Page
def resultPage(request):
    obj=Teacher.objects.get(tUser=request.user)
    test=Test.objects.filter(teacherId=obj.tid,approved=1)
    resultDetails=[]
    for i in test:
        if(datetime.datetime.now().timestamp()>=i.start.timestamp()):
            resultDetails.append([i.testId,i.subject,i.topic])
    data={'resultDetails':resultDetails}
    return render(request,"resultPage.html",data)

@csrf_exempt
#View All Results
def viewAllResults(request):
    test=Test.objects.filter(approved=1)
    resultDetails=[]
    for i in test:
        if(datetime.datetime.now().timestamp()>=i.start.timestamp()):
            resultDetails.append([i.testId,i.subject,i.topic])
    data={'resultDetails':resultDetails}
    return render(request,"viewAllResults.html",data)

@csrf_exempt
#View Result Page
def viewResultPage(request,testId):
    obj=StudentResults.objects.filter(testId=testId)
    resultList=[]
    for i in obj:
        stObj=Student.objects.get(stid=i.stid)
        resultList.append([stObj.email,i.scoredMarks,i.submitDate.date(),i.stid,i.testGivenId])
    return render(request,'viewResultPage.html',{'resultList':resultList,'testId':testId})

@csrf_exempt
#View Result
def viewResult(request,testId):
    obj=StudentResults.objects.filter(testId=testId)
    resultList=[]
    for i in obj:
        stObj=Student.objects.get(stid=i.stid)
        resultList.append([stObj.email,i.scoredMarks,i.submitDate.date(),i.stid,i.testGivenId])
    return render(request,'viewResult.html',{'resultList':resultList,'testId':testId})

@csrf_exempt
#Approve Quiz
def approveQuiz(request,testId):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            tObj=Test.objects.get(testId=testId)
            tObj.approved=1
            tObj.save()
            messages.success(request,testId+ "has been approved")
            return redirect("/approveQuizPage/")
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt   
#Delete Quiz
def deleteQuiz(request,testId):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            tObj=Test.objects.get(testId=testId)
            qObj=Questions.objects.filter(testId=testId)
            for i in qObj:
                i.delete()
            messages.success(request,testId+ "has been rejected")
            tObj.delete()
            return redirect("/approveQuizPage/")
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                messages.error(request,"You don't have access !!")
                return redirect("/")
    else:
        return redirect('/adminLoginPage/')

@csrf_exempt    
#Student Profile Page
def studentProfilePage(request):
    if request.user.is_authenticated:
        try:
            adUser=Admin.objects.get(adUser=request.user)
            messages.error(request,request.user+ "you don't have access")
            return redirect("/adminDashboard/")
        except:
            try:
                obj=Teacher.objects.get(tUser=request.user)
                messages.error(request,"You don't have access !!")
                return redirect("/teacherDashboard/")
            except:
                obj=StudentProfile.objects.filter(spUser=request.user)
                if not obj:
                    messages.error(request,"Profile not created")
                    return render(request,"createStudentProfilePage.html")
                else:
                    sp=StudentProfile.objects.get(spUser=request.user)
                    name=sp.name
                    mob=sp.mob
                    interestedCourse=sp.interestedCourse
                    address=sp.address
                    picture=sp.picture
                    course=interestedCourse.split(",")
                    return render(request,"studentProfilePage.html",{'name':name,'mob':mob,'course':course,'address':address,'picture':picture})
    else:
        return redirect('/studentLoginPage/')

@csrf_exempt
#Edit Profile Page
def editProfilePage(request):
    sp=StudentProfile.objects.get(spUser=request.user)
    name=sp.name
    mob=sp.mob
    interestedCourse=sp.interestedCourse
    address=sp.address
    picture=sp.picture
    return render(request,"editProfilePage.html",{'name':name,'mob':mob,'interestedCourse':interestedCourse,'address':address,'picture':picture})

@csrf_exempt
#Create Student Profile
def createStudentProfile(request):
    name = request.POST.get("name")
    mobile = request.POST.get("mobile")
    C = request.POST.get("C")
    Cpp = request.POST.get("C++")
    Java = request.POST.get("Java")
    Python = request.POST.get("Python")
    address = request.POST.get("address")
    img = request.FILES.get("img")
    course=""
    if(C=='1'):
        course+="C,"
    if(Cpp=='1'):
        course+="C++,"
    if(Java=='1'):
        course+="Java,"
    if(Python=='1'):
        course+="Python"
    handle_uploaded_student_file(img)
    obj=Student.objects.get(stUser=request.user)
    a=StudentProfile.objects.create(spUser=request.user,email=obj.email,name=name,mob=mobile,interestedCourse=course,address=address,picture="studentPics/"+img.name)
    messages.success(request,"Profile Created Successfully")
    return redirect("/studentProfilePage/")

@csrf_exempt
#Update Student Profile
def updateStudentProfile(request):
    name = request.POST.get("name")
    mobile = request.POST.get("mobile")
    interestedCourse=request.POST.get("interestedCourse")
    address = request.POST.get("address")
    obj=StudentProfile.objects.get(spUser=request.user)
    obj.name=name
    obj.mob=mobile
    obj.interestedCourse=interestedCourse
    obj.address=address
    obj.save()
    messages.success(request,"Profile Updated Successfully")
    return redirect("/studentProfilePage/")

@csrf_exempt
#Edit Profile Picture
def editProfilePicturePage(request):
    obj=StudentProfile.objects.get(spUser=request.user)
    picture=obj.picture
    return render(request,"editProfilePicturePage.html",{'picture':picture})

@csrf_exempt    
#Update Student Profile Picture
def updateStudentProfilePicture(request):
    img = request.FILES.get("img")
    handle_uploaded_student_file(img)
    obj=StudentProfile.objects.get(spUser=request.user)
    obj.picture="studentPics/"+img.name
    obj.save()
    messages.success(request,"Profile Picture Updated Successfully")
    return redirect("/studentProfilePage/")

@csrf_exempt   
#Interested Students List
def interestedStudentsList(request):
    tObj=Teacher.objects.get(tUser=request.user)
    course=tObj.course
    stObj=StudentProfile.objects.all()
    studentList=[]
    for i in stObj:
        if course in i.interestedCourse:
            studentList.append([i.email,i.name,i.mob])
    return render(request,"interestedStudentsList.html",{'studentList':studentList})

@csrf_exempt
#Students List
def studentsList(request):
    stObj=StudentProfile.objects.all()
    studentList=[]
    for i in stObj:
        studentList.append([i.email,i.name,i.mob])
    return render(request,"studentsList.html",{'studentList':studentList})

@csrf_exempt
#Teachers List
def teachersList(request):
    tObj=Teacher.objects.all()
    teacherList=[]
    for i in tObj:
        teacherList.append([i.email,i.fname+" "+i.lname,i.mob])
    return render(request,"teachersList.html",{'teacherList':teacherList})

@csrf_exempt
#View Student Details
def viewStudentDetails(request,email):
    stObj=StudentProfile.objects.get(email=email)
    data={'name':stObj.name,'email':stObj.email,'mob':stObj.mob,'interestedCourse':stObj.interestedCourse.split(','),'address':stObj.address,'picture':stObj.picture}
    return render(request,"viewStudentDetails.html",data)

@csrf_exempt
#View Teacher Details
def viewTeacherDetails(request,email):
    tObj=Teacher.objects.get(email=email)
    data={'name':tObj.fname+" "+tObj.lname,'email':tObj.email,'mob':tObj.mob,'course':tObj.course,'address':tObj.address,'picture':tObj.picture}
    return render(request,"teacherDetails.html",data)

@csrf_exempt
#Student Subscribe Page
def studentSubscribePage(request):
    if request.user.is_authenticated:
        sObj=Student.objects.get(stUser=request.user)
        obj=Subscribe.objects.filter(stid=sObj.stid)
        if not obj:
            currency = 'INR'
            amount = 50000  # Rs. 500
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                            currency=currency,
                                                            payment_capture='0'))
            # order id of newly created order.
            # print(razorpay_order['id'])
            razorpay_order_id = razorpay_order['id']
            callback_url = 'http://127.0.0.1:8000/subscribe/'
        
            # we need to pass these details to frontend.
            context = {}
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url
 
            return render(request, 'studentSubscribePage.html', context=context)
        else:
            found=0
            for i in obj:
                given_date = datetime.datetime.fromtimestamp(i.subscribeDate.timestamp())
                # Get current date
                current_date = datetime.datetime.now()
                # Calculate the difference in days
                difference_in_days = (current_date - given_date).days
                if difference_in_days<180:
                    found=1
            if found==0:
                currency = 'INR'
                amount = 50000  # Rs. 500
                    # Create a Razorpay Order
                razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                                    currency=currency,
                                                                    payment_capture='0'))
                    # order id of newly created order.
                    # print(razorpay_order['id'])
                razorpay_order_id = razorpay_order['id']
                callback_url = 'http://127.0.0.1:8000/subscribe/'
                
                    # we need to pass these details to frontend.
                context = {}
                context['razorpay_order_id'] = razorpay_order_id
                context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
                context['razorpay_amount'] = amount
                context['currency'] = currency
                context['callback_url'] = callback_url
        
                return render(request, 'studentSubscribePage.html', context=context)
            else:    
                messages.error(request,"Already Subscribed")
                return redirect("/")
    else:
        return redirect("/studentLoginPage/")

@csrf_exempt
#Subscribe
def subscribe(request):
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 50000  # Rs. 500
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    sObj=Student.objects.get(stUser=request.user)
                    obj=Subscribe.objects.create(sUser=request.user,stid=sObj.stid,email=sObj.email,subscribeDate=datetime.datetime.now(),paymentId=payment_id,razorpayOrderId=razorpay_order_id,signature=signature)
                    # render success page on successful caputre of payment
                    messages.success(request,"Subscribed Successfully")
                    return redirect("/")
                except:
                    # if there is an error while capturing payment.
                    print("Error 1")
                    
                    messages.error(request,"Error in Payment")
                    return redirect("/")
            else:
 
                # if signature verification fails.
                print("Error 2")
                
                messages.error(request,"Error in Payment")
                return redirect("/")
        except:
 
            # if we don't find the required parameters in POST data
            print("Error 3")
            messages.error(request,"Error in Payment")
            return redirect("/")
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()
    
@csrf_exempt
#Student Forgot Password Page
def studentForgotPasswordPage(request):
    return render(request,"studentForgotPasswordPage.html")

@csrf_exempt
#Admin Forgot Password Page
def adminForgotPasswordPage(request):
    return render(request,"adminForgotPasswordPage.html")

@csrf_exempt
#Teacher Forgot Password Page
def teacherForgotPasswordPage(request):
    return render(request,"teacherForgotPasswordPage.html")

@csrf_exempt
#Student Forgot Password 
def studentForgotPassword(request):
    email=request.POST.get("email")
    try:
        adUser=Admin.objects.get(email=email)
        messages.error(request,email+ " not found !!!")
        return redirect("/studentForgotPasswordPage/")
    except:
        try:
            obj=Teacher.objects.get(email=email)
            messages.error(request,email+ " not found !!!")
            return redirect("/studentForgotPasswordPage/")
        except:
            try:
                obj=Student.objects.get(email=email)
                otp=generateOTP()
                ForgotPasswordOTP(email,otp)
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
                expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
                request.session["details"]={'stemail':email,"otp":otp,'expiryTime':expiryTime}
                messages.success(request, 'Please check your mail for OTP ')
                return redirect("/studentForgotPasswordPage/")                
            except:
                messages.error(request,email+ " not found !!!")
                return redirect("/studentForgotPasswordPage/")
            
@csrf_exempt
#Admin Forgot Password 
def adminForgotPassword(request):
    email=request.POST.get("email")
    try:
        adUser=Student.objects.get(email=email)
        messages.error(request,email+ " not found !!!")
        return redirect("/adminForgotPasswordPage/")
    except:
        try:
            obj=Teacher.objects.get(email=email)
            messages.error(request,email+ " not found !!!")
            return redirect("/adminForgotPasswordPage/")
        except:
            try:
                obj=Admin.objects.get(email=email)
                otp=generateOTP()
                ForgotPasswordOTP(email,otp)
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
                expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
                request.session["details"]={'ademail':email,"otp":otp,'expiryTime':expiryTime}
                messages.success(request, 'Please check your mail for OTP ')
                return redirect("/adminForgotPasswordPage/")                
            except:
                messages.error(request,email+ " not found !!!")
                return redirect("/adminForgotPasswordPage/")
            
@csrf_exempt
#Teacher Forgot Password 
def teacherForgotPassword(request):
    email=request.POST.get("email")
    try:
        adUser=Admin.objects.get(email=email)
        messages.error(request,email+ " not found !!!")
        return redirect("/teacherForgotPasswordPage/")
    except:
        try:
            obj=Student.objects.get(email=email)
            messages.error(request,email+ " not found !!!")
            return redirect("/teacherForgotPasswordPage/")
        except:
            try:
                obj=Teacher.objects.get(email=email)
                otp=generateOTP()
                ForgotPasswordOTP(email,otp)
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=300)
                expiryTime = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
                request.session["details"]={'temail':email,"otp":otp,'expiryTime':expiryTime}
                messages.success(request, 'Please check your mail for OTP ')
                return redirect("/teacherForgotPasswordPage/")                
            except:
                messages.error(request,email+ " nor found !!!")
                return redirect("/teacherForgotPasswordPage/")
            
@csrf_exempt
#Teacher Reset Password Page
def teacherResetPasswordPage(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    sotp=details["otp"]
    if(eotp==sotp):
        temail=details["temail"]
        del request.session["details"]
        return render(request,"teacherResetPasswordPage.html",{"temail":temail})
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/teacherForgotPasswordPage/") 
    
@csrf_exempt
#Student Reset Password Page
def studentResetPasswordPage(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    sotp=details["otp"]
    if(eotp==sotp):
        stemail=details["stemail"]
        del request.session["details"]
        return render(request,"studentResetPasswordPage.html",{"stemail":stemail})
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/studentForgotPasswordPage/") 
    
@csrf_exempt
#Admin Reset Password Page
def adminResetPasswordPage(request):
    eotp=request.POST.get("otp")
    details=request.session["details"]
    sotp=details["otp"]
    if(eotp==sotp):
        ademail=details["ademail"]
        del request.session["details"]
        return render(request,"adminResetPasswordPage.html",{"ademail":ademail})
    else:
        messages.error(request,"Invalid OTP")
        return redirect("/adminForgotPasswordPage/") 
    
@csrf_exempt
#Student Reset Password
def studentResetPassword(request,email):
    password=request.POST.get("password")
    obj=User.objects.get(username=email)
    obj.set_password(password)
    obj.save()
    messages.success(request,"Password reset Successfully!!!")
    return redirect("/studentLoginPage/")

@csrf_exempt
#Admin Reset Password
def adminResetPassword(request,email):
    password=request.POST.get("password")
    obj=User.objects.get(username=email)
    obj.set_password(password)
    obj.save()
    messages.success(request,"Password reset Successfully!!!")
    return redirect("/adminLoginPage/")

@csrf_exempt
#Teacher Reset Password
def teacherResetPassword(request,email):
    password=request.POST.get("password")
    obj=User.objects.get(username=email)
    obj.set_password(password)
    obj.save()
    messages.success(request,"Password reset Successfully!!!")
    return redirect("/teacherLoginPage/")