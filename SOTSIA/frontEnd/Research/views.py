from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/sotsia/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/sotsia/login/')
def testing(request):
    return render(request, 'sotsia/testing.html')
    # url = 'http://localhost:5000/dataset/dbName'
    # res = requests.request(method="GET", url=url)
    # list_dict = res.json()
    # list_dbName = []
    # for dict in list_dict:
    #     for key,value in dict.items():
    #         list_dbName.append(value) 
    # url = 'http://localhost:5000/dataset/data'
    # res = requests.request(method="GET", url=url)
    # data_db = res.json()
    # if request.user.is_authenticated:
    #     args = {'user_authenticated' : 'true', 'database_name':list_dbName, 'data':data_db }
    #     template = 'sotsia/testing.html'
    # else:
    #     args = {'user_authenticated' : 'false' }
    #     template = 'sotsia/testing-fail.html'
    # return render(request, 'sotsia/testing.html', args)


@login_required(login_url='/sotsia/login/')
def dataset(request):
    return render(request, 'sotsia/dataset.html')


@login_required(login_url='/sotsia/login/')
def reports(request):
    return render(request, 'sotsia/reports.html')