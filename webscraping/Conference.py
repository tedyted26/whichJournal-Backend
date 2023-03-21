class Conference:
    def __init__(self, url:str,
                 titulo:str,
                 descripcion: str,
                 temas:str,
    fecha:str,
    ubicacion:str,
    fechaEntrega:str,
    organizacion:str,
    tipo:str,
    tags:str,
    precio:str):
        self.url = url
        self.titulo = titulo
        self.descripcion = descripcion
        self.temas = temas
        self.fecha = fecha
        self.ubicacion = ubicacion
        self.fechaInscripcion = fechaEntrega
        self.organizacion:str = organizacion
        self.tipo:str = tipo
        self.tags:str = tags
        self.precio:str = precio