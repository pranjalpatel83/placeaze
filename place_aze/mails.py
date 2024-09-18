from django.conf import settings
from django.core.mail import send_mail


#Student Verification Mail
def studentVerificationOTP(email,otp):
    try:
        subject="Verify your Account"
        message= f'Hey, {email}\nYour Verificaion OTP is:- {otp}'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

#Forgot Password Mail
def ForgotPasswordOTP(email,otp):
    try:
        subject="Forgot Password OTP"
        message= f'Hey, {email}\nYour OTP is:- {otp}'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

#Teacher Verification Mail
def teacherVerificationOTP(email,otp):
    try:
        subject="Verify your Account"
        message= f'Hey, {email}\nYour Verificaion OTP is:- {otp}'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

#Admin Verification Mail
def adminVerificationOTP(email,otp):
    try:
        subject="Admin Verification"
        message= f'Hey, {email}\nYour Verificaion OTP is:- {otp}'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

#Teacher Acceptation Mail
def teacherAccept(email):
    try:
        subject="Approved"
        message= f'Hey, {email}\nYou have been Approved by the admin.\nKindly Login at Teacher login.'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

#Teacher Rejection Mail
def teacherReject(email):
    try:
        subject="Rejected"
        message= f'Hey, {email}\nYou have been rejected by the admin.'
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True