import os.path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from flux.constants import appbase
from flux.models import Collection
from flux.view.foundations import *

@login_required
# This operation is redundant, we save changes each step.
def collection_save(request):
    #collection_name = request.session['collection_name']
    #save_collection_to_disk(request.user, collection_name, pathway)
    return HttpResponse(content = """Collection saved """, status = 200, content_type = "text/html")

@login_required
def collection_create(request):
    """ Give a name of this collection, save it somewhere """
    collection_name = request.GET['collection_name']
    bac_name = request.GET['bacteria'].split()[0]
    email = request.GET['email']
    try:
        collection = Collection.objects.get(name = collection_name, user = request.user)
        return HttpResponse(content = """Collection name is already in use """, status = 200, content_type = "text/html")
    except Collection.DoesNotExist:
        pathway = None
        if bac_name == "TOY":
            import cPickle
            f = open(appbase + 'toy/toy_pathway.pickle', 'rb')
            pathway = cPickle.load(f)
            f.close()
        else:
            pathway = generate_pathway(bac_name, collection_name)
        if request.user == None:
            print "Collection create requires login"
        save_collection_to_disk(request.user, collection_name, pathway)

        # request.session['pathway'] = pathway
        request.session['collection_name'] = collection_name
        request.session['email'] = email
        request.session['provided_email'] = email
        return HttpResponse(content = """Collection created """, status = 200, content_type = "text/html")
    else:
        return HttpResponse(content = """Collection name is already in use """, status = 404, content_type = "text/html")

@login_required
def collection_saveas(request):
    """ User will rename a collection """
    collection_name = request.session['collection_name']
    new_name = request.GET['new_name']
    rename_collection(request.user, collection_name, new_name)
    request.session['collection_name'] = new_name
    return HttpResponse(content = """ Collection renamed. """, status = 200, content_type = "text/html")

@login_required
def collection_select(request):
    """ Select PathwayNetwork for a given user"""
    collection_name = request.GET['collection_name']
    pathway = get_pathway_by_name(request.user, collection_name)
    if pathway:
        request.session['collection_name'] = collection_name
        return HttpResponse(content = """Collection selected """, status = 200, content_type = "text/html")
    else:
        return HttpResponse(content = """Can not find designated collection """, status = 200, content_type = "text/html")

@login_required
def collection_summary(request):
    names = get_collection_names(request.user)
    result = " ".join(names)
    return HttpResponse(content = result, status = 200, content_type = "text/html")

