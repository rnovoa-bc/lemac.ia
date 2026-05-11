import json

def prepara():
    """
    Legirem un fitxer ISO2709 amb les dades de la LEMAC
    i el convertirem a un format JSON que serà més fàcil d'utilitzar per entrenar el model.
    """

    for registre in llegir_registres_iso():
    

def llegir_registres_iso():
    """
    Funció per llegir els registres del fitxer ISO2709 i convertir-los a un format JSON.
    """
    fitxer_iso = "data/lemac_data.iso"
    fitxer_json = "data/lemac_data.json"
    with open(fitxer_iso, "r") as f:
        buffer = b""
        while tros = f.read(8192)
        parts = tros.split(b"\x1d")  # Separador de registres en ISO2709
        for registre in partsþ[:-1]:
            yield registre
        
        buffer = parts[-1]

    if buffer:
        yield buffer

def analitza_registre(registre):
    """
    Funció per processar un registre ISO2709 i convertir-lo a un format diccionari.
    """
    capacalera = registre[:24]
    final_directori = reggistre.find(b"\x1e")
    directori = registre[24:final_directori]
    dades = registre[final_directori+1:]

    for i in range(0, len(directori), 12):
        tag = directori[i:i+3].decode("utf-8")
        longitud = int(directori[i+3:i+7])
        posicio = int(directori[i+7:i+11])
        camp_dades = dades[posicio:posicio+longitud]
        # Aquí podem processar el camp_dades segons el tag i extreure la informació que necessitem
    