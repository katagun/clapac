class CraigslistApartmentListing:


    def __init__(self):
        self.properties = { 
            "datapid":       None, 
            "datetime":      None, 
            "title":         None, 
            "housing" :      None, 
            "ft" :           None,
            "ad_url" :       None, 
            "hood" :         None, 
            "zipcode" :      None, 
            "bedrooms" :     None, 
            "bathrooms" :    None,
            "price" :        None,
            "map_location" : None 
        }


    def __setitem__(self, key, value):
        self.properties[key] = value


    def __getitem__(self, key):
        return self.properties[key]


    def __str__(self):
        retstr = "|".join(str(v).rstrip().lstrip() for v in self.properties.values())
        return retstr
