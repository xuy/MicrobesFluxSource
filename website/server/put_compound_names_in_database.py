import cPickle
import sys, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microbesflux.settings")

from flux.constants import appbase
from flux.models import Compound
from flux.parser.helper import *

def put_data_in():
    data = read_pickle(appbase + 'kegg/compound_lite.pk')
    alias = data[0]
    longname = data[1]

    for key in alias:
        a = alias[key]
        l = longname.get(key, "")
        c = Compound(name = key, alias = a, long_name = l)
        c.save()

def query(n):
    c = Compound.objects.get(name__exact=n)
    print c

def long_name_query(n):
    c = Compound.objects.get(long_name__exact=n)
    print c

if __name__ == "__main__":
    size = len(Compound.objects.all())
    if not size:
        print "Initializing Compounds table using flux/compound_list.pk..."
        put_data_in()
        print "Done putting data into database."

    query("C15064")
    long_name_query("Ethylmalonyl-CoA")
    long_name_query("H2O")
