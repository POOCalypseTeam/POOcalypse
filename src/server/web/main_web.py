import wsinter

window_width = 1080
window_height = 720

last_img_id = 0
       
def add_image(path: str, position: tuple, size: tuple=None):
    """
    Ajoute l'image pointee par path sur la page
    
    Parametres:
    
        - path : Chemin vers l'image relatif au dossier /src/content
        - position : Position pour l'image sur la page sous la forme d'un tuple (x, y)
        - size : Taille de l'image, 0 pour la taille native de l'image, sous la forme d'un tuple (w, h)
    
    Renvoie l'id de l'image
    """
    global last_img_id
    
    style = {"position": "absolute", "left": str(position[0]) + "px", "top": str(position[1]) + "px"}
    if size != None:
        style["width"] = str(size[0]) + "px"
        style["height"] = str(size[1]) + "px"
    img_id = "img" + str(last_img_id)
    ws.insere(img_id, "img", attr={'src':f'../{path}'}, style=style)
    last_img_id += 1
    return img_id    
    
def change_dimensions(id: str, position: tuple=None, size: tuple=None):
    if position == None and size == None:
        raise ValueError("BRUH, faut mettre des valeurs quand meme")
    style = {"position": "absolute"}
    if position != None:
        style["left"] = str(position[0]) + "px"
        style["top"] = str(position[1]) + "px"
    if size != None:
        style["width"] = str(size[0]) + "px"
        style["height"] = str(size[1]) + "px"  
    ws.attributs(id, style=style)
    
def change_text(id: str, new_text: str):
    ws.attributs(id, )

def remove_html(id: str):
    # TODO: Bien supprimer l'élément au lieu de le cacher
    # demander modification wsinter car demande du JS mais pas opti de fare des injecte
    # car ca créé un element script a chaque fois, pas renta
    ws.attributs(id, style={"display": "none"})

def set_window_size(_, size: list):
    """
    Actualise la taille de la page Web
    
    Ne prend pas effet sur l'affichage dans le navigateur
    
    Utilise seulement par le gestionnaire d'evenement lors d'un appel par le client
    """
    global window_width
    global window_height

    window_width = size[0]
    window_height = size[1]
    
def get_window_size():
    """
    Recupere la taille de la page Web
    """
    global window_width
    global window_height
    return (window_width, window_height)


def start() -> wsinter.Inter:
    global ws
    ws = wsinter.Inter()
    ws.demarre(page="content/pages/index.html", clavier=True)
    
    # Permet d'avoir la taille de la fenetre en temps reel
    ws.gestionnaire("get_window_size", set_window_size)
    ws.injecte("""
window.addEventListener("resize", (e) => {
   transmettre("get_window_size", [window.innerWidth, window.innerHeight]); 
});
""")
    # On la recupere une fois au debut
    ws.injecte('transmettre("get_window_size", [window.innerWidth, window.innerHeight]);')
    
    return ws
    
