from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from django.views import View

from ..decorators import student_required
from ..forms import StudentInterest, StudentSignUp, TakeTestForm
from ..models import Test, Student, TakenQuiz, User, Question


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUp
    template_name = 'signupform.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')


@method_decorator([login_required, student_required], name='dispatch')
class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterest
    template_name = 'student/interests_form.html'
    success_url = reverse_lazy('students:quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class SQuizListView(ListView):
    model = Test
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'student/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.tests.values_list('pk', flat=True)
        queryset = Test.objects.filter(topic__in=student_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class SQuizResultsView(View):
    template_name = 'student/quiz_result.html'

    def get(self, request, *args, **kwargs):        
        quiz = Test.objects.get(id = kwargs['pk'])
        taken_quiz = TakenQuiz.objects.filter(student = request.user.student, test = quiz)
        if not taken_quiz:
            """
            Don't show the result if the user didn't attempted the quiz
            """
            return render(request, '404.html')
        questions = Question.objects.filter(test =quiz)
        
        # questions = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'questions':questions, 
            'test':quiz, 'percentage': taken_quiz[0].percentage})


@method_decorator([login_required, student_required], name='dispatch')
class STakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_test'
    template_name = 'student/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_test \
            .select_related('test', 'test__topic') \
            .order_by('test__name')
        return queryset


@login_required
@student_required
def Stake_quiz(request, pk):
    quiz = get_object_or_404(Test, pk=pk)
    student = request.user.student

    if student.tests.filter(pk=pk).exists():
        return render(request, 'student/taken_quiz_list.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeTestForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('students:take_quiz', pk)
                else:
                    correct_answers = student.test_answer.filter(answer__question__test=quiz, answer__correct=True).count()
                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(student=student, test=quiz, score=correct_answers, percentage= percentage)
                    student.score = TakenQuiz.objects.filter(student=student).aggregate(Sum('score'))['score__sum']
                    student.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, percentage))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, percentage))
                    return redirect('students:quiz_list')
    else:
        form = TakeTestForm(question=question)

    return render(request, 'student/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })