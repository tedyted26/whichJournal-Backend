class Journal:
    def __init__(self, url:str,
    imagePath:str,
    title:str,
    description: str,
    issn:str,
    type:str,
    price:str,
    impactFactor:float,
    quartil:str,
    otherMetric:float,
    nameOtherMetric:str,
    acceptanceRate:str,
    timeDecision:str,
    timePublication:str,
    timeReview:str,
    origin: str,
    indexing: list):
        self.url = url
        self.imagePath = imagePath
        self.title = title
        self.description = description
        self.issn = issn
        self.type = type
        self.price = price
        self.impactFactor = impactFactor
        self.quartil = quartil
        self.otherMetric = otherMetric
        self.nameOtherMetric = nameOtherMetric
        self.acceptanceRate = acceptanceRate
        self.timeDecision = timeDecision
        self.timePublication = timePublication
        self.timeReview = timeReview
        self.origin = origin
        self.indexing = indexing