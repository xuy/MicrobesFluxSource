from flux.models import Compound

# This file uses mysql database to replace the old ReactionDB
class CompoundDB:
    def is_a_valid_name(self, n):
        try:
            c = Compound.objects.get(long_name__exact=n)
            return True
        except Compound.MultipleObjectsReturned:
            return False
        except Compound.DoesNotExist:
            pass
        try:
            c = Compound.objects.get(name__exact = n)
            if len(c.long_name) < 1:
                return False
            else:
                return True
        except Compound.DoesNotExist:
            return False

    def get_long_name(self, sname):
        try:
            c = Compound.objects.get(name__exact = sname)
            if len(c.long_name) < 1:
                a = c.alias
                c = Compound.objects.get(name__exact = a)
            return c.long_name
        except Compound.DoesNotExist:
            return sname
