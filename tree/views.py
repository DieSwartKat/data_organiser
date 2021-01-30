from django.shortcuts import render
from libraries.treetool.treetool import AllpartsJson
from dataorg.settings import BASE_DIR
from .models import ProjectParts
import os

def home_page(request):
    # file = os.path.join(BASE_DIR, 'data', 'treetool.txt')
    # allparts = AllpartsJson(treetool_location=file).allparts
    # parts = []
    # for part in allparts:
    #     x = ProjectParts(part=part, prt_class=allparts[part]["PRT_CLASS"], mat_desc=allparts[part]["MAT_DESC"])
    #     try:
    #         x.save()
    #     except:
    #         print(part)
    parts = ProjectParts.objects.all()
    
    return render(request, "index.html", {'data' : parts})


