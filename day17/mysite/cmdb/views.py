from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse

from cmdb import models
# Create your views here.

def index(request):
    #return HttpResponse('MySite!')
    data_list = models.UserInfo.objects.all()
    return render(request,'index.html',{'data':data_list})

def demo(request):
    return render(request,'demo/index.html')

def login(request):

    status = {'status':False}
    #如果客户端提交的是post,先获取用户的用户名,密码
    if(request.method == 'POST'):
        #获取用户提交的用户名密码
        u = request.POST.get('username')
        p = request.POST.get('p')
        # print('Username: %s\nPassword: %s'%(u,p))
        res = models.UserInfo.objects.filter(username=u)
        #print(res,type(res))
        if res:
            for i in res:
                if(i.username == u and i.passwd == p):
                    return redirect('/demo/')
                   #return render(request,'index.html')
        status[status] = '账号/密码错误!'
        return HttpResponse()

    return render(request,'login.html')

    #return HttpResponse(request,'login.html')

def regist(request):
    #如果客户端提交的是post,先获取用户的用户名,密码
    if(request.method == 'POST'):
        u = request.POST.get('user',None)
        p = request.POST.get('passwd',None)
        q = request.POST.get('qq',None)
        models.UserInfo.objects.create(username=u,passwd=p,qq=q)

        return HttpResponse('注册成功!')

def services(request):
    return render(request,'services.html')
    #return HttpResponse(request,'login.html')

