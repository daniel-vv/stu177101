from django.shortcuts import render
from django.shortcuts import HttpResponse
from article.models import Article
from django.http import Http404

# Create your views here.

def demo(request):
    return HttpResponse('Hello World!')


def home(request):
    post_list = Article.objects.all()
    return render(request, 'home.html',{'post_list':post_list})
    #return HttpResponse('Hello World! Django')

def detail(request,id):
    #post = Article.objects.all()[int(my_args)]
    # str = ("title = %s, category = %s, date_time = %s, content = %s"
    #        %(post.title, post.category, post.date_time, post.content))
    #
    # return HttpResponse(str)
    try:
        post = Article.objects.get(id=str(id))
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'post.html', {'post' : post})

