from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView


class IndexView(TemplateView):
    template_name = 'mamogourmet/index.html'
