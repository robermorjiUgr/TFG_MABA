from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from numpy import empty
from .models import DatasetConfiguration, Experiment
from django.shortcuts import get_object_or_404

from datetime import datetime, time, timedelta
from django.utils.timezone import make_aware

import requests
from base64 import encodebytes, decodebytes
import io, os
from django.core.files.images import ImageFile

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  

# Create your views here.
@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')


def api_request(function):
    result = ''
    try:
        url = 'http://localhost:5000/sotsia/' + function
        result = requests.request(method="GET", url=url)
        print("Connection successful with the API")
    except:
        print("Error trying to access the API")
    return result


@login_required(login_url='/login/')
def research(request):
    args = {}
    now = make_aware(datetime.now())
    one_week_ago = make_aware(datetime.now() - timedelta(days=7))

    # Database names
    result = api_request('get-db-names-sizes')
    print(result)
    res_json = result.json()['db_sizes']
    key_list = []
    print(res_json[0].keys())
    for key in res_json[0].keys(): 
        key_list.append(key)
        try:
            # Database size with 2 decimals only (MB)
            res_json[0][key] = "{:.2f}".format(res_json[0][key] / (1024*1024))
        except:
            print("Error")
    args['databases'] = key_list
    args['db_size'] = res_json[0]

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

    # Database names and keys
    result = api_request('get-db-names-meta')
    res_json = result.json()['meta_keys']
    key_list = []
    for key in res_json[0].keys(): 
        key_list.append(key)
    args['databases'] = key_list
    args['db_keys'] = res_json[0]

    # Min and Max dates
    result = api_request('/ICPE/get-min-max-date')
    # Get the date in datetime format so the template doesn't read it as a string
    min_date = datetime.strptime(result.json()['min_date'], "%a, %d %b %Y %H:%M:%S %Z").date()
    args['min_date'] = min_date
    max_date = datetime.strptime(result.json()['max_date'], "%a, %d %b %Y %H:%M:%S %Z").date()
    args['max_date'] = max_date

    if request.method == "POST":
        args['message'] = ''
        database = request.POST.get('select_database', '')
        types = request.POST.getlist('types', '')
        types_list = ''
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
                    dataset = DatasetConfiguration(
                                database=database, 
                                start_date=start_date, 
                                end_date=end_date, 
                                author=request.user.username, 
                                types_selected=types_list
                    )
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

    if request.method == "POST":
        delete_list = request.POST.getlist('delete')        
        # Check if list is empty
        if len(delete_list) != 0:
            for report_id in delete_list:
                report = Experiment.objects.get(id=report_id)
                report.delete()
        else:
            print("You haven't checked any report")
        return redirect('/reports/')

    return render(request, 'sotsia/reports.html', args)


@login_required(login_url='/login/')
def algorithm(request):
    args = {}

    # result = api_request('get-db-names')
    # print(result)
    # dbs_list = result.json()['databases']
    # args['databases'] = dbs_list

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

    if request.method == "POST":
        delete_list = request.POST.getlist('delete')        
        # Check if list is empty
        if len(delete_list) != 0:
            for report_id in delete_list:
                report = DatasetConfiguration.objects.get(id=report_id)
                report.delete()
        else:
            print("You haven't checked any dataset")
        return redirect('/deep-learning/')

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
        args['specific_algorithms'].append('LSTM')
    elif request.build_absolute_uri().find("data-mining") != -1:
        parent = '/data-mining'
        algorithm = 'Data Mining'
        args['specific_algorithms'].append('Algorithm 1')
    elif request.build_absolute_uri().find("machine-learning") != -1:
        parent = '/machine-learning'
        algorithm = 'Machine Learning'
        args['specific_algorithms'].append('Support Vector Machine')
    args['algorithm'] = algorithm
    args['parent'] = parent

    dataset = get_object_or_404(DatasetConfiguration, pk=request.GET.get('dataset-id'))
    if dataset.author == request.user.username:
        args['access'] = 1
        args['dataset'] = dataset
        types_list = dataset.types_selected.split('; ')
        types_list[-1] = types_list[-1][:-1]            # Last item only have a ';', not '; '
        args['dataset_types'] = types_list

        if request.method == "POST":
            args['message'] = ''
            algorithm_specific = request.POST.get('select_algorithm', '')
            description = request.POST.get('description', '')
            database = dataset.database
            start_date = dataset.start_date
            end_date = dataset.end_date

            if algorithm_specific == 'lstm':
                start_date = start_date.strftime('%Y-%m-%d')
                end_date = end_date.strftime('%Y-%m-%d')
                url = 'deep-learning/lstm/{}?start_date={}&end_date={}&id_sensor=9093'.format(database, start_date, end_date)
                print(url)
                # start = time()
                result = api_request(url)
                # end = time.time()
                # total_time = start - end

                if result==None or result=='Error':
                    args['message'] = 'There was an error during the execution'
                    args['message_type'] = 'error'
                    print(result.content)
                else:
                    args['message'] = 'The experiment was a success'
                    args['message_type'] = 'correct'
                    #print(result.content)
                    experiment_number = Experiment.objects.count() + 1
                    image = ImageFile(io.BytesIO(result.content), name='LSTM_exp_{}.jpg'.format(experiment_number))
                    experiment = Experiment(
                        database=dataset.database,
                        algorithm_group=algorithm, 
                        algorithm_specific=algorithm_specific, 
                        start_date=datetime.now(),
                        description=description,
                        duration=time(0, 2, 45), 
                        dataset=dataset,
                        result=image
                        )
                    print(experiment)
                    experiment.save()
    # Don't have access to the page
    else:
        args['message'] = 'You don\'t have access to this page'
        args['message_type'] = 'error'
        args['access'] = 0
    return render(request, 'sotsia/experimentation.html', args)


@login_required(login_url='/login/')
def document(request, id):
    args = {}
    host = "http://127.0.0.1:8000"

    report = get_object_or_404(Experiment, pk=id)
    if report.dataset.author == request.user.username:
        args['access'] = 1
        args['report_id'] = report.id
        args['report'] = report
        args['image'] = host + str(report.result).split("Research",1)[1]
    else:
        args['message'] = 'You don\'t have access to this page'
        args['message_type'] = 'error'
        args['access'] = 0
    return render(request, 'sotsia/document.html', args)


# defining the function to convert an HTML file to a PDF file
def html_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None


#@login_required(login_url='/login/')
def generate_pdf(request, id):
    args = {}
    host = "http://127.0.0.1:8000"

    report = get_object_or_404(Experiment, pk=id)
    args['report'] = report
    # The path of the image is /static/images/experiments/
    args['image'] = host + str(report.result).split("Research",1)[1]

    # getting the template
    pdf = html_to_pdf('sotsia/doc_to_pdf.html', args)
        
    # rendering the template
    return HttpResponse(pdf, content_type='application/pdf')