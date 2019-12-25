"""alphaslate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from school.views import home,SignUpView
from django.contrib.auth import views as auth_views
from school.view.admin import TeacherSignUpView,QuizListView,QuizCreateView,QuizUpdateView,QuizDeleteView,QuizResultsView,question_add,question_change,QuestionDeleteView
from school.view.student import StudentSignUpView,SQuizListView,StudentInterestsView,STakenQuizListView,Stake_quiz,SQuizResultsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/signup/student/', StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/signup/teacher/', TeacherSignUpView.as_view(), name='teacher_signup'),


    path('teachers/', include(([
        path('', QuizListView.as_view(), name='quiz_change_list'),
        path('quiz/add/', QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),
    ], 'classroom'), namespace='teachers')),

    path('students/', include(([
        path('', SQuizListView.as_view(), name='quiz_list'),
        path('interests/', StudentInterestsView.as_view(), name='student_interests'),
        path('taken/', STakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', Stake_quiz, name='take_quiz'),        
        path('quiz/<int:pk>/studentresults/', SQuizResultsView.as_view(), name='student_quiz_results'),
    ], 'classroom'), namespace='students')),
]
