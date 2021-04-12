from django.http import HttpResponse


def index(request):
    return HttpResponse("Disk1, Disk2 etc")

