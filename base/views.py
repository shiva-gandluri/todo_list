from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, FormView #To tell django how you want to display the view
from .models import Task
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin # similar to decorators that are used to restrict unauthourized users
from django.contrib.auth.forms import UserCreationForm #registration form
from django.contrib.auth import login

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView): #FormView is used to display the below defined view

    #cusomizing basic registration page
    template_name = 'base/register.html'
    form_class = UserCreationForm #UserCreationForm is the structure of registration form
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks' #setting the default object name from 'object_list' to 'tasks'

    def get_context_data(self, **kwargs): #method to change context of a particular view. Just like context dictionary in function based views
        context = super().get_context_data(**kwargs) 
        context['tasks'] = context['tasks'].filter(user=self.request.user) #filtering data as per user logged in
        context['count'] = context['tasks'].filter(complete=False).count() #getting the count of unfinished tasks in to-do list

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task' #setting the defaullt object name from 'object' to 'task'
    template_name = 'base/task.html' #setting the defaullt template name 'task_detail.html' to 'task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks') #used to redirect to url with name = 'tasks'

    #customizinf below in-built method to show user specific data
    def form_valid(self, form): #will be triggered automatically when this view is called
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')
            
            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))