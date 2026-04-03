from django import forms
from .models import Ticket
from apps.departments.models import Department


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = [
            'department', 'type', 'subtype', 'subject', 'description',
            'priority', 'url_system', 'steps', 'normal_behavior',
            'unexpected_behavior', 'justification', 'acceptance_criteria',
            'manual_process', 'automation_name', 'notify_by_email',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'steps': forms.Textarea(attrs={'rows': 3}),
            'normal_behavior': forms.Textarea(attrs={'rows': 3}),
            'unexpected_behavior': forms.Textarea(attrs={'rows': 3}),
            'justification': forms.Textarea(attrs={'rows': 3}),
            'acceptance_criteria': forms.Textarea(attrs={'rows': 3}),
            'manual_process': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            if user.role in ('admin', 'atendente'):
                self.fields['department'].queryset = Department.objects.filter(active=True)
            else:
                from apps.accounts.models import UserDepartment
                dept_ids = UserDepartment.objects.filter(user=user).values_list('department_id', flat=True)
                self.fields['department'].queryset = Department.objects.filter(id__in=dept_ids, active=True)

        # Campos condicionais — não obrigatórios por padrão
        conditional_fields = [
            'url_system', 'steps', 'normal_behavior', 'unexpected_behavior',
            'justification', 'acceptance_criteria', 'manual_process', 'automation_name',
        ]
        for field in conditional_fields:
            self.fields[field].required = False
            
        # Adiciona classes do Bootstrap em todos os campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'