from django.shortcuts import render
from .models import CI
from django.views.generic import ListView, DetailView


class CIListView(ListView):
    model = CI


class CIDetailView(DetailView):
    model = CI
