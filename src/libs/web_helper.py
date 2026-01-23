import wsinter

class Helper:
    def __init__(self, ws: wsinter.Inter):
        """
        Initialise une nouvelle instance de Helper avec l'instance de WSInter en argument
        """
        self.ws = ws

        self.last_img_id: int = 0

    def add_image(self, path: str, position: tuple, size: tuple = None, zindex: int = 0, parent: str = "body"):
        """
        Ajoute l'image pointee par path sur la page
        
        Parametres:
            - path: Chemin vers l'image relatif au dossier /src/content
            
            - position: Position pour l'image sur la page sous la forme d'un tuple (x, y)
            
            - size: Taille de l'image, 0 pour la taille native de l'image, sous la forme d'un tuple (w, h)
            
            - z_index: Précision sur l'organisation devant/derrière des images sous forme d'un entier

            - parent: L'id de l'element parent sur la page Web, body par defaut
            
        Renvoie l'id de l'image
        """        
        style = {"position": "absolute", "left": str(position[0]) + "px", "top": str(position[1]) + "px"}
        if size != None:
            style["width"] = str(size[0]) + "px"
            style["height"] = str(size[1]) + "px"
        style["z-index"] = str(zindex)
        img_id = "img" + str(self.last_img_id)
        self.ws.insere(img_id, "img", attr={'src':f'../{path}'}, style=style, parent=parent)
        self.last_img_id += 1
        return img_id
    
    def change_image(self, id, img):
        self.ws.attributs(id, attr = {'src' : f'../{img}'})
    
    def change_dimensions(self, id: str, position: tuple = None, size: tuple = None):
        """
        Change la position et ou la taille de l'element dans la page

        Parametres:
            - id: L'id de l'element dont les proprietes sont a changer

            - position: Tuple de la forme (x,y) donnant la nouvelle position de l'element

            - size: Tuple de la forme (w,h) donnant la nouvelle taille de l'element
        """
        if position == None and size == None:
            raise ValueError("Aucune valeur renseignee")
        style = {"position": "absolute"}
        if position != None:
            style["left"] = str(position[0]) + "px"
            style["top"] = str(position[1]) + "px"
        if size != None:
            style["width"] = str(size[0]) + "px"
            style["height"] = str(size[1]) + "px"  
        self.ws.attributs(id, style=style)

    def change_text(self, id: str, new_text: str):
        """
        Change l'attribut `innerText` de l'element

        Parametres:

            - id: L'id de l'element a modifier

            - new_text: Nouveau texte a remplacer
        """
        self.ws.inner_text(id, new_text)

    def remove_html(self, id: str):
        """
        Supprime l'element de la page
        """
        self.ws.remove(id)