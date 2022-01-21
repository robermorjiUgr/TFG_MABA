from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def testing(request):
    if request.user.is_authenticated:
        args = {'user_authenticated' : 'true' }
        template = 'sotsia/testing.html'
    else:
        args = {'user_authenticated' : 'false' }
        template = 'sotsia/testing-fail.html'
    return render(request, 'sotsia/testing.html', args)