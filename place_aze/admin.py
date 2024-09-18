from django.contrib import admin
from .models import Student,LoggedInUser,Admin,Teacher,Questions,Test,StudentProfile,Subscribe,StudentAns,StudentResults

admin.site.register(Student)
admin.site.register(Admin)
admin.site.register(Teacher)
admin.site.register(LoggedInUser)
admin.site.register(Questions)
admin.site.register(Test)
admin.site.register(StudentResults)
admin.site.register(StudentAns)
admin.site.register(StudentProfile)
admin.site.register(Subscribe)


