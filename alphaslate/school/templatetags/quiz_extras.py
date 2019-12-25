from django import template
from ..models import StudentAnswer
register = template.Library()



@register.simple_tag
def marked_answer(user,opt):
    studentanswer = StudentAnswer.objects.filter(student=user.student, answer =opt)
    if studentanswer:
        if opt.correct:
            return 'correct'
        return 'wrong'

    return 