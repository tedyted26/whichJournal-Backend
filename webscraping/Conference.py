class Conference:
    def __init__(self, titulo:str,
    fecha:str,
    pais:str,
    ciudad:str,
    fechaInscripcion:str,
    organizacion:str,
    tipo:str,
    tags:str,
    precio:str):
        self.titulo = titulo
        self.fecha = fecha
        self.pais = pais
        self.ciudad = ciudad
        self.fechaInscripcion = fechaInscripcion
        self.organizacion:str = organizacion
        self.tipo:str = tipo
        self.tags:str = tags
        self.precio:str = precio