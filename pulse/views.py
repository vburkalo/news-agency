from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from pulse.models import Topic, Redactor, Newspaper
from pulse.forms import TopicForm, RedactorForm, NewspaperForm, NewspaperSearchForm


def index(request: HttpRequest) -> HttpResponse:
    num_topics = Topic.objects.count()
    num_redactors = Redactor.objects.count()
    num_newspapers = Newspaper.objects.count()
    context = {
        "num_topics": num_topics,
        "num_redactors": num_redactors,
        "num_newspapers": num_newspapers,
    }
    return render(request, "pulse/index.html", context)


class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    template_name = "pulse/topic_list.html"


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = Topic
    form_class = TopicForm
    template_name = "pulse/topic_form.html"
    success_url = reverse_lazy("pulse:topics")


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "pulse/topic_form.html"
    success_url = reverse_lazy("pulse:topics")


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    template_name = "pulse/topic_confirm_delete.html"
    success_url = reverse_lazy("pulse:topics")


class RedactorListView(LoginRequiredMixin, generic.ListView):
    model = Redactor
    template_name = "pulse/redactor_list.html"
    context_object_name = "redactors"


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Redactor
    template_name = "pulse/redactor_detail.html"
    context_object_name = "redactor"


class RedactorCreateView(LoginRequiredMixin, generic.CreateView):
    model = Redactor
    form_class = RedactorForm
    success_url = reverse_lazy("pulse:redactors")


class RedactorUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Redactor
    form_class = RedactorForm
    success_url = reverse_lazy("pulse:redactors")


class RedactorDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Redactor
    template_name = "pulse/redactor_confirm_delete.html"
    success_url = reverse_lazy("pulse:redactors")


class NewspaperListView(LoginRequiredMixin, generic.ListView):
    model = Newspaper
    template_name = "pulse/newspaper_list.html"
    context_object_name = "newspaper_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = NewspaperSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = NewspaperSearchForm(self.request.GET)
        if form.is_valid():
            pass
        return queryset


class NewspaperDetailView(LoginRequiredMixin, generic.DetailView):
    model = Newspaper
    template_name = "pulse/newspaper_detail.html"


class NewspaperCreateView(LoginRequiredMixin, generic.CreateView):
    model = Newspaper
    form_class = NewspaperForm
    success_url = reverse_lazy("pulse:newspapers")


class NewspaperUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Newspaper
    form_class = NewspaperForm
    success_url = reverse_lazy("pulse:newspapers")


class NewspaperDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Newspaper
    template_name = "pulse/newspaper_confirm_delete.html"
    success_url = reverse_lazy("pulse:newspapers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['newspaper'] = Newspaper.objects.get(pk=self.kwargs['pk'])
        return context
