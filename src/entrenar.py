import torch

class Entrenament:
    """
    Classe per gestionar l'entrenament d'un model utilitzant
    PyTorch i Transformers
    """
    def __init__(self):
        # Farem ús de la GPU si existeix
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

def entrenar_model():
    entrenament = Entrenament()
    print(f"Utilitzant dispositiu: {entrenament.device}")
    # Aquí aniria el codi per carregar les dades, definir el model,
    # configurar l'entrenament i executar-lo
    