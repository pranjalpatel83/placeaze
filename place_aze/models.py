from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class LoggedInUser(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,related_name='logged_in_user',on_delete=models.CASCADE)
    session_key=models.CharField(max_length=32,blank=True,null=True)
    
    def __str__(self):
        return self.user.username

class Student(models.Model):
    stid=models.AutoField(primary_key=True)
    stUser= models.ForeignKey(User, on_delete=models.CASCADE)
    email=models.EmailField(blank=False,null=False)

    def __str__(self):
        return self.email
    
class StudentProfile(models.Model):
    spid=models.AutoField(primary_key=True)
    spUser= models.ForeignKey(User, on_delete=models.CASCADE)
    email=models.EmailField(blank=False,null=False)
    name=models.CharField(max_length=55,null=False)
    mob=models.IntegerField(max_length=10,null=False)
    interestedCourse=models.CharField(max_length=100,null=False)
    address=models.CharField(max_length=255,null=False)
    picture=models.ImageField(upload_to='studentPics/',null=False)

    def __str__(self):
        return self.email
    
    
class Teacher(models.Model):
    tid=models.AutoField(primary_key=True)
    tUser= models.ForeignKey(User, on_delete=models.CASCADE)
    email=models.EmailField(blank=False,null=False)
    fname=models.CharField(max_length=30,null=False)
    lname=models.CharField(max_length=20,null=False)
    mob=models.IntegerField(max_length=10,null=False)
    course=models.CharField(max_length=20,null=False)
    address=models.CharField(max_length=255,null=False)
    picture=models.ImageField(upload_to='teacherPics/',null=False)
    
    def __str__(self):
        return self.email

class Admin(models.Model):
    adUser= models.ForeignKey(User, on_delete=models.CASCADE)
    email=models.EmailField(blank=False,null=False)

    def __str__(self):
        return self.email

class Questions(models.Model):
    qUid=models.BigAutoField(primary_key=True)
    testId=models.CharField(max_length=20)
    qId=models.CharField(max_length=25)
    q=models.TextField()
    a=models.CharField(max_length=100)
    b=models.CharField(max_length=100)
    c=models.CharField(max_length=100)
    d=models.CharField(max_length=100)
    ans=models.CharField(max_length=10)
    marks=models.IntegerField()
    teacherId=models.BigIntegerField()
    
    def __str__(self):
        return self.qId
    
class StudentAns(models.Model):
    saUid=models.BigAutoField(primary_key=True)
    qUid=models.BigIntegerField()
    testId=models.CharField(max_length=20)
    stid=models.IntegerField()
    markedAns=models.CharField(max_length=10)
    ans=models.CharField(max_length=10)
    marks=models.IntegerField()
    testGivenId=models.CharField(max_length=100)
    
    
    def __str__(self):
        return self.testId
    

class StudentResults(models.Model):
    srUid=models.BigAutoField(primary_key=True)
    stid=models.IntegerField()
    testId=models.CharField(max_length=20)
    scoredMarks=models.IntegerField()
    submitDate=models.DateTimeField(auto_now_add=True)
    testGivenId=models.CharField(max_length=100)
    
    
    def __str__(self):
        return self.testId
    
      
class Test(models.Model):
    tUid=models.BigAutoField(primary_key=True)
    email=models.CharField(max_length=100)
    testId=models.CharField(max_length=100)
    start=models.DateTimeField(auto_now_add=True)
    end=models.DateTimeField()
    duration=models.IntegerField()
    subject=models.CharField(max_length=100)
    topic=models.CharField(max_length=100)
    teacherId=models.BigIntegerField()
    approved=models.IntegerField()
    
    def __str__(self):
        return self.testId
    
class Subscribe(models.Model):
    sUid=models.BigAutoField(primary_key=True)
    sUser= models.ForeignKey(User, on_delete=models.CASCADE)
    stid=models.IntegerField(blank=False,null=False)
    email=models.EmailField(blank=False,null=False)
    subscribeDate=models.DateTimeField(auto_now_add=True)
    paymentId=models.CharField(max_length=255)
    razorpayOrderId=models.CharField(max_length=255)
    signature=models.CharField(max_length=255)
    