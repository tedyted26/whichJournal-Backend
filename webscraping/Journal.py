class Journal:
    def __init__(self, url:str,
    imagePath:str,
    title:str,
    description: str,
    issn:str,
    releaseYear:str,
    type:str,
    price:str,
    impactFactor:str,
    quartil:str,
    otherMetric:str,
    nameOtherMetric:str,
    acceptanceRate:str,
    timeDecision:str,
    timePublication:str,
    timeReview:str,
    origin: str,
    otherInfo: str):
        self.url = url
        self.imagePath = imagePath
        self.title = title
        self.description = description
        self.issn = issn
        self.releaseYear = releaseYear
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
        self.otherInfo = otherInfo