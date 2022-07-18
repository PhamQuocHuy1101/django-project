from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def myview(request):
    cur = request.COOKIES.get('count', 0)
    cur = int(cur)
    resp = render(request, 'hello/index.html', context = {'cookie': '714bb9ae', 'count': cur + 1})
    resp.set_cookie('dj4e_cookie', '714bb9ae', max_age=1000)
    resp.set_cookie('count', cur + 1, max_age=1000)

    return resp