from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DatasetConfiguration

from datetime import datetime

# Create your views here.
@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def research(request):
    args = {}
    args['scientists'] = User.objects.count()
    return render(request, 'sotsia/research.html', args)


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


def date_is_valid(date):
    try:
        date = datetime.strptime(date, "%d/%m/%Y")
        return True
    except ValueError:
        return False

@login_required(login_url='/login/')
def dataset(request):
    args = {}
    # Modificar esto cuando se añada la conexión a la BD
    args['databases'] = []
    args['databases'].append('Resources and Energy')
    args['databases'].append('Medical')
    args['databases'].append('ICPE')
    args['types'] = []
    args['types'].append('Name')
    args['types'].append('Surname')
    args['types'].append('Address')
    args['types'].append('Telephone')
    args['types'].append('Country')
    args['message'] = ''

    if request.method == "POST":
        args['message'] = 'POST'
        types = request.POST.getlist('types', '')
        types_list = ''
        print(request.POST.get('start_date', ''))
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        if date_is_valid(start_date) and date_is_valid(end_date):
            # Dates are in a valid format "DD/MM/YYYY"
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
            if start_date < end_date:
                # Start date is before the end date 
                if types == '':
                    args['message'] = 'You must check at least one type to create a new dataset'
                    args['message_type'] = 'error'
                else:
                    for item in types:
                        types_list += item + '; '
                    # Remove last space from string
                    types_list = types_list[:-1]
                    args['message'] = 'The dataset has been correctly created'
                    args['message_type'] = 'correct'
                    # Create the model and save it
                    dataset = DatasetConfiguration(database="Resources and Energy", start_date=start_date, end_date=end_date, author=request.user.username, types_selected=types_list)
                    dataset.save()
            else:
                args['message'] = 'The starting date must be before the ending date'
                args['message_type'] = 'error'
        else:
            args['message'] = 'Incorrect date format, use the correct format: "DD/MM/YYYY"'
            args['message_type'] = 'error'
    return render(request, 'sotsia/dataset.html', args)


@login_required(login_url='/login/')
def reports(request):
    return render(request, 'sotsia/reports.html')

@login_required(login_url='/login/')
def algorithm(request):
    args = {}
    algorithm = ''
    if request.build_absolute_uri().find("deep-learning") != -1:
        algorithm = 'Deep Learning'
    elif request.build_absolute_uri().find("data-mining") != -1:
        algorithm = 'Data Mining'
    elif request.build_absolute_uri().find("machine-learning") != -1:
        algorithm = 'Machine Learning'
    args['algorithm'] = algorithm

    datasets = DatasetConfiguration.objects.all()
    my_datasets = []
    for i in datasets:
        if i.author == request.user.username:
            my_datasets.append(i)
    args['datasets'] = my_datasets

    return render(request, 'sotsia/algorithm.html', args)

@login_required(login_url='/login/')
def experimentation(request):
    args = {}
    algorithm = ''
    parent = ''
    if request.build_absolute_uri().find("deep-learning") != -1:
        parent = '/deep-learning'
        algorithm = 'Deep Learning'
    elif request.build_absolute_uri().find("data-mining") != -1:
        parent = '/data-mining'
        algorithm = 'Data Mining'
    elif request.build_absolute_uri().find("machine-learning") != -1:
        parent = '/machine-learning'
        algorithm = 'Machine Learning'
    args['algorithm'] = algorithm
    args['parent'] = parent

    return render(request, 'sotsia/experimentation.html', args)