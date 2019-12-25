from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ..decorators import teacher_required
from ..forms import BaseAnswerInlineFormSet, QuestionForm, AdminSignUp
from ..models import Answer, Question, Test, User


class TeacherSignUpView(CreateView):
    model = User
    form_class = AdminSignUp
    template_name = 'signupform.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'admin'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('teachers:quiz_change_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizListView(ListView):
    model = Test
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'admin/testchangelist.html'

    def get_queryset(self):
        print('lol',self.request.user)
        queryset = self.request.user.tests \
            .select_related('topic') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_test', distinct=True))
        return queryset


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Test
    fields = ('name', 'topic', )
    template_name = 'admin/testadd.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('teachers:quiz_change', quiz.pk)


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Test
    fields = ('name', 'topic', )
    context_object_name = 'quiz'
    template_name = 'admin/testChange.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.tests.all()

    def get_success_url(self):
        return reverse('teachers:quiz_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Test
    context_object_name = 'quiz'
    template_name = 'admin/testDelete.html'
    success_url = reverse_lazy('teachers:quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Test
    context_object_name = 'quiz'
    template_name = 'admin/testResult.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_test.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_test.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.tests.all()


@login_required
@teacher_required
def question_add(request, pk):
    quiz = get_object_or_404(Test, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('teachers:question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'admin/add.html', {'quiz': quiz, 'form': form})


@login_required
@teacher_required
def question_change(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Test, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, test=quiz)

    AnswerFormSet = inlineformset_factory(
        Question, 
        Answer,  
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True

    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('teachers:quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'admin/change.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'admin/delete.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.test
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(test__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:quiz_change', kwargs={'pk': question.test_id})