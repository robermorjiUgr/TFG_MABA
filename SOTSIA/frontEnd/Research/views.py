from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def testing(request):
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
    return render(request, 'sotsia/testing.html')

def dataset(request):
    return render(request, 'sotsia/dataset.html')