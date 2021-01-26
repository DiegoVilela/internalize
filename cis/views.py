from django.shortcuts import render
from .models import CI, Client
from django.views.generic import ListView, DetailView


class ClientListView(ListView):
    model = Client


class ClientDetailView(DetailView):
    model = Client


class CIListView(ListView):
    model = CI


class CIDetailView(DetailView):
    model = CI
