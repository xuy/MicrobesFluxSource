from view.json import Json

"""
    # TODO
    2. filter out the plus sign 
"""

def parse_reaction_part(compond_string):
    comp_list = compond_string.split('+')
    coef   = []
    result = []
    for comp in comp_list:
        test = comp.split()
        if len(test) == 1:
            coef.append(1.0)
            name = test[0]
        else:
            coef.append(float(test[0]))
            name = test[1]
    result.append(name)
    return (coef, result)
    
class Reaction:
    
    def __init__(self, name):
        self.name = name
        self.longname_map = {}
        self.reversible = False
        self.products = []
        self.substrates = []
        self.stoichiometry = {}
        self.ko = False
        self.metabolism = None
        self.active = True
        
    def __repr__(self):
        return self.name + str(self.reversible) + ' '.join(map(str, self.products)) + ' '.join(map(str, self.substrates))

    def _get_long_name(self, s):
        """ Get the descriptive name for a compound """	
        if self.longname_map.has_key(s):
            return self.longname_map[s]
        else:
            return s
    
    def set_metabolism_name(self, m):
        self.metabolism = m
    
    """ Generate a human-readable string that represents this reaction.
    	This function is used by Report. """
    def quick_view(self):
        l = []
        if self.ko:
            l.append(" X ")
        else:
            l.append("   ")
        l.append(self.name)
        l.append(" : ")
        s = []
        for t in self.substrates:
            s.append(str(self.stoichiometry[t]) + ' ' + self._get_long_name(t))
        l.append(' + '.join(s))
        if self.reversible:
            l.append(' <--> ')
        else:
            l.append(' ---> ')
        s = []
        for t in self.products:
            s.append(str(self.stoichiometry[t]) + ' ' + self._get_long_name(t))
        l.append(' + '.join(s))
        return ''.join(l)

    def get_substrates_as_long_names(self):
        r = []
        for t in self.substrates:
            r.append(str(self._get_long_name(t)))
        return r
    def get_products_as_long_names(self):
        r = []
        for t in self.products:
            r.append(str(self._get_long_name(t)))
        return r

    def getJson(self):
        """ Return a JSON object representing this reaction. """
        r = Json("object")
        r.add_pair("reactionid", self.name)
        s = []
        for t in self.substrates:
            s.append(str(self.stoichiometry[t]) + ' ' + self._get_long_name(t))
        r.add_pair("reactants", " + ".join(s))
        s = []
        for t in self.products:
            s.append(str(self.stoichiometry[t]) + ' ' + self._get_long_name(t))
        r.add_pair("products", " + ".join(s))
        if self.reversible:
            r.add_pair("arrow", "<==>")
        else:
            r.add_pair("arrow", "===>")

        ko_label = Json()
        ko_label.set_label('"ko"')
        ko_value = Json()

        if self.ko:
            ko_value.set_label("true")
        else:
            ko_value.set_label("false")

        r.add_pair(ko_label, ko_value)
        if self.metabolism:
            r.add_pair("pathway", self.metabolism)
        return r
    
