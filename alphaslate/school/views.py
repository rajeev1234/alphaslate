from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('teachers:quiz_change_list')
        else:
            return redirect('students:quiz_list')
    return render(request, 'home.html')