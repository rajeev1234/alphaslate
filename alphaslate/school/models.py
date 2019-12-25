from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import escape, mark_safe

# Create your models here.

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default= False)

class Topic(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=10,default='#007bff')

    def __str__(self):
        return self.name

    def get_htm_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-prmary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)

class Test(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tests")
    name= models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tests')

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question',max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    correct = models.BooleanField('Correct Answer', default= False)

    def __str__(self):
        return self.text

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, primary_key= True)
    tests = models.ManyToManyField(Test, through='TakenQuiz')
    interests = models.ManyToManyField(Topic, related_name="interested_student")
    score = models.IntegerField(default=0)

    # def get_unanswered_questions(self,test):
    def __str__(self):
        return self.user.username

    
    def get_unanswered_questions(self, quiz):
        answered_questions = self.test_answer \
            .filter(answer__question__test=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions


class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="taken_test")
    test = models.ForeignKey(Test, on_delete= models.CASCADE, related_name= 'taken_test')
    score = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete= models.CASCADE, related_name="test_answer")
    answer = models.ForeignKey(Answer, on_delete= models.CASCADE, related_name='+')
