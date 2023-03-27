class Conference:
    def __init__(self, url:str,
                 titulo:str,
                 descripcion: str,
                 temas:list,
    fecha:str,
    ubicacion:str,
    fechaInscripcion:str,
    organizacion:str,
    tipo:str,
    tags:list,
    precio:str,
    origen:str):
        self.url = url
        self.titulo = titulo
        self.descripcion = descripcion
        self.temas = temas
        self.fecha = fecha
        self.ubicacion = ubicacion
        self.fechaInscripcion = fechaInscripcion
        self.organizacion = organizacion
        self.tipo = tipo
        self.tags = tags
        self.precio = precio
        self.origen = origen