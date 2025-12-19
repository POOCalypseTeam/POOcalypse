import wsinter
from time import sleep
from random import randint

y = 100
x = 100

window_width = 1080
window_height = 720

last_img_id = 0

# faire sauter l'image quand on clic dessus
def jump(s,d):
    global x,y
    if s=="D":
        if d[0]=='img01':
            x=randint(0,800)
            y=randint(0,800)
            ws.attributs('img01',style={"left":str(x)+"px","top":str(y)+"px"})

def animer():
    global x
    while x < 800:
        sleep(0.05)
        x+=1
        ws.attributs('img01',style={"left":str(x)+"px"})
       
def add_image(path: str, position: tuple, size: tuple=None, zindex: int=None, parent=None):
    """
    Ajoute l'image pointee par path sur la page
    
    Parametres:
    
        - path : Chemin vers l'image relatif au dossier /src/content
        - position : Position pour l'image sur la page sous la forme d'un tuple (x, y)
        - size : Taille de l'image, 0 pour la taille native de l'image, sous la forme d'un tuple (w, h)
        - zindex : Précision sur l'organisation devant/derrière des images sous forme d'un entier
        
    Renvoie l'id de l'image
    """
    global last_img_id
    
    style = {"position": "absolute", "left": str(position[0]) + "px", "top": str(position[1]) + "px"}
    if size != None:
        style["width"] = str(size[0]) + "px"
        style["height"] = str(size[1]) + "px"
    if zindex != None:
        style["z-index"] = str(zindex)
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
    
