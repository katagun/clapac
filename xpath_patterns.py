class CraigsListApaXpathPatterns:


    def __init__(self):
        self.patterns = {}
        result_info = "p[@class='result-info']/"
        result_meta = "span[@class='result-meta']/"
        self.patterns["rows"] = r"//ul[@class='rows']/li[@class='result-row']"
        self.patterns["datetime"] = result_info + "time[@class='result-date']/@datetime"
        self.patterns["title"]    = result_info + "a[@class='result-title hdrlnk']/text()"
        self.patterns["datapid"]   = result_info + "a[@class='result-title hdrlnk']/@data-id"
        self.patterns["housing"] = result_info + result_meta + "span[@class='housing']/text()"
        self.patterns["ad_url"]  = result_info + "a[@class='result-title hdrlnk']/@href"
        self.patterns["price"]  = result_info + result_meta + "span[@class='result-price']/text()"
        self.patterns["hood"]    = result_info + result_meta + "span[@class='result-hood']/text()"
        paginator = r"//div[@class='paginator buttongroup firstpage']"
        paginator += "/span[@class='buttons']/"
        self.patterns['next_url'] = paginator + "a[@class='button next']/@href"
