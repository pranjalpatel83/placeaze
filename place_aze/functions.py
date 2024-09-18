#Hande Uploaded File
def handle_uploaded_file(f):
    with open('media/teacherPics/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
#Hande Uploaded File
def handle_uploaded_student_file(f):
    with open('media/studentPics/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)