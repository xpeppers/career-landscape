from django.views import generic

class AboutView(generic.TemplateView):
    template_name = "clusters/about.html"