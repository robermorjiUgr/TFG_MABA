from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DatasetConfiguration, Experiment
from django.shortcuts import get_object_or_404

from datetime import datetime, time, timedelta
from django.utils.timezone import make_aware

import requests

# Create your views here.
@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='/login/')
def research(request):
    args = {}
    now = make_aware(datetime.now())
    one_week_ago = make_aware(datetime.now() - timedelta(days=7))

    url = 'http://localhost:5000/sotsia/get-db-names'
    res = requests.request(method="GET", url=url)
    dbs_list = res.json()['databases']
    args['databases'] = dbs_list

    args['scientists'] = User.objects.count()
    users_this_week = User.objects.filter(date_joined__gte=one_week_ago, date_joined__lt=now).count()
    args['scientists_week'] = users_this_week

    args['experiments'] = Experiment.objects.count()
    experiments_this_week = Experiment.objects.filter(created_at__gte=one_week_ago, created_at__lt=now).count()
    args['experiments_week'] = experiments_this_week

    args['datasets'] = DatasetConfiguration.objects.count()
    datasets_this_week = DatasetConfiguration.objects.filter(created_at__gte=one_week_ago, created_at__lt=now).count()
    args['datasets_week'] = datasets_this_week

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
        # Check if dates are in the valid format "YYYY-MM-DD"
        date = datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@login_required(login_url='/login/')
def dataset(request):
    args = {}
    args['message'] = ''

    # Databases
    url = 'http://localhost:5000/sotsia/get-db-names'
    res = requests.request(method="GET", url=url)
    dbs_list = res.json()['databases']
    args['databases'] = dbs_list

    # Types
    url = 'http://localhost:5000/sotsia/ICPE/get-collection-keys'
    res = requests.request(method="GET", url=url)
    types_list = res.json()['keys']
    args['types'] = types_list

    if request.method == "POST":
        args['message'] = ''
        types = request.POST.getlist('types', '')
        types_list = ''
        print(request.POST.get('start_date', ''))
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        if date_is_valid(start_date) and date_is_valid(end_date):
            # Dates are in a valid format "YYYY-MM-DD"
            print("Is valid")
            print(type(start_date))
            print(start_date)
            print(type(end_date))
            print(end_date)
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
            args['message'] = 'Incorrect date format, use the correct format: "YYYY-MM-DD"'
            args['message_type'] = 'error'
    return render(request, 'sotsia/dataset.html', args)


@login_required(login_url='/login/')
def reports(request):
    args = {}
    experiments = Experiment.objects.all()
    experiments_list = []

    for item in experiments:
        if item.dataset.author == request.user.username:
            experiments_list.append(item)

    args['experiments'] = experiments_list

    return render(request, 'sotsia/reports.html', args)


@login_required(login_url='/login/')
def algorithm(request):
    args = {}
    args['databases'] = []
    args['databases'].append('Resources and Energy')
    args['databases'].append('Medical')
    args['databases'].append('ICPE')
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
    args['specific_algorithms'] = []
    if request.build_absolute_uri().find("deep-learning") != -1:
        parent = '/deep-learning'
        algorithm = 'Deep Learning'
        args['specific_algorithms'].append('Algorithm 1')
        args['specific_algorithms'].append('Algorithm 2')
        args['specific_algorithms'].append('Algorithm 3')
    elif request.build_absolute_uri().find("data-mining") != -1:
        parent = '/data-mining'
        algorithm = 'Data Mining'
        args['specific_algorithms'].append('Algorithm 1')
        args['specific_algorithms'].append('Algorithm 2')
        args['specific_algorithms'].append('Algorithm 3')
    elif request.build_absolute_uri().find("machine-learning") != -1:
        parent = '/machine-learning'
        algorithm = 'Machine Learning'
        args['specific_algorithms'].append('Algorithm 1')
        args['specific_algorithms'].append('Algorithm 2')
        args['specific_algorithms'].append('Algorithm 3')
    args['algorithm'] = algorithm
    args['parent'] = parent

    dataset = get_object_or_404(DatasetConfiguration, pk=request.GET.get('dataset-id'))
    args['dataset'] = dataset
    types_list = dataset.types_selected.split('; ')
    types_list[-1] = types_list[-1][:-1]            # Last item only have a ';', not '; '
    args['dataset_types'] = types_list

    if request.method == "POST":
        args['message'] = ''
        algorithm_specific = request.POST.get('select_algorithm', '')
        description=request.POST.get('description', '')
        experiment = Experiment(
            algorithm_group=algorithm, 
            algorithm_specific=algorithm_specific, 
            start_date=datetime.now(),
            description=description,
            duration=time(0, 2, 45), 
            dataset=dataset)
        experiment.save()

    return render(request, 'sotsia/experimentation.html', args)


@login_required(login_url='/login/')
def document(request, id):
    args = {}
    report = get_object_or_404(Experiment, pk=id)
    args['report_id'] = report.id
    args['report'] = report

    return render(request, 'sotsia/document.html', args)