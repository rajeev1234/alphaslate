from django.contrib import admin

# Register your models here.
from .models import User, Topic, Test, Question, Answer,Student, TakenQuiz, StudentAnswer

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Student)
admin.site.register(TakenQuiz)
admin.site.register(StudentAnswer)