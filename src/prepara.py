import json
import requests



def prepara():
    """
    Legirem un fitxer ISO2709 amb les dades de la LEMAC
    i el convertirem a un format JSON que serà més fàcil d'utilitzar per entrenar el model.
    """
    comptador = 0
    registes = []
    for registre in llegir_registres_iso():
        registre_processat = analitza_registre(registre)
        if registre_processat is None:
            continue
        registre_net = classifica_marc21(registre_processat)
        registes.append(registre_net)
        comptador += 1

        if comptador % 100 == 0 and comptador > 0:
            print(f"Processats {comptador} registres...", end="\r")
        if comptador == 200:
            break
            
    with open("dades/lemac.json", "w", encoding="utf-8") as f:
        json.dump(registes, f, ensure_ascii=False, indent=2)
    

def llegir_registres_iso():
    """
    Funció per llegir els registres del fitxer ISO2709 i convertir-los a un format JSON.
    """
    fitxer_iso = "dades/lemac.iso"
    fitxer_json = "dades/lemac.json"
    with open(fitxer_iso, "rb") as f:
        buffer = b""
        while tros := f.read(8192):
            buffer += tros
            parts = buffer.split(b"\x1d")  # Separador de registres en ISO2709
            for registre in parts[:-1]:
                yield registre
        
            buffer = parts[-1]

    if buffer:
        yield buffer

def analitza_registre(registre):
    """
    Funció per processar un registre ISO2709 i convertir-lo a un format diccionari.
    """
    try:
        capacalera = registre[:24]
        final_directori = registre.find(b"\x1e")
        directori = registre[24:final_directori]
        dades = registre[final_directori+1:]

        # sordida la guaradem al diccionari etiquetes
        etiquetes = {}

        for i in range(0, len(directori), 12):
            entrada = directori[i:i+12]
            tag = entrada[:3].decode("utf-8")
            longitud = int(entrada[3:7].decode("utf-8"))
            inici = int(entrada[7:].decode("utf-8"))
            camp_dades = dades[inici:inici+longitud-1]  # El camp de dades acaba amb un separador de camps (0x1e)
            # Aquí podem processar el camp_dades segons el tag i extreure la informació que necessitem
            if tag.startswith("00"):
                # caps de control
                value = camp_dades.decode("utf-8")
                etiquetes.setdefault(tag, []).append(value)
            else:
                # camps d'informació
                indicadors = camp_dades[:2].decode("utf-8")
                subcamps_dades = camp_dades[2:]
                subcamps = {}
                for subcamp in subcamps_dades.split(b"\x1f")[1:]: # Els subcamps comencen amb un separador de subcamp (0x1f)
                    if subcamp:
                        codi = subcamp[:1].decode("utf-8")
                        valor = subcamp[1:].decode("utf-8")
                        subcamps.setdefault(codi, []).append(valor)
                etiqueta = {"indicadors": indicadors, "subcamps": subcamps}
                etiquetes.setdefault(tag, []).append(etiqueta)

        return { "capacalera": capacalera, "etiquetes": etiquetes }
    except Exception as e:
        print(f"Error processant el registre: {e}")
        return None

def imprimir_registre(registre):
    """
    Funció per imprimir un registre en pantalla per depurar analiza_registre.
    """
    print("#"*80)
    print(f"Capçalera: {registre["capacalera"].decode("utf-8")}")
    for tag, contingut in registre["etiquetes"].items():
        for item in contingut:
            if isinstance(item, dict):
                print(f"Etiqueta: {tag}; Indicadors: {item['indicadors'].replace(" ", "□")}")
                for codi, valors in item["subcamps"].items():
                    for valor in valors:
                        print(f"  ${codi} {valor}")
            else:
                print(f"Control {tag}: {contingut}")

def classifica_marc21(registre):
    """
    Funció per convertir un registre processat a un format JSON.
    """
    registre_json = {}
    for tag, contingut in registre["etiquetes"].items():
        for etiqueta in contingut:
            if tag in ["100", "110", "111", "130", "150", "151", "155"]:
                encapcalament = etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz")
                registre_json.setdefault("terme_acceptat", []).append(encapcalament)
                registre_json["titols"] = obtenir_titols(encapcalament)
            elif tag in ["400", "410", "411", "430", "450", "451", "455"]:
                registre_json.setdefault("terme_no_acceptat", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
            elif tag in ["180"]:
                registre_json.setdefault("subd_tematica", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
            elif tag in ["480"]:
                registre_json.setdefault("subd_tematica_no_acceptada", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
            elif tag in ["185"]:
                registre_json.setdefault("subd_forma", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
            elif tag in ["485"]:   
                registre_json.setdefault("subd_forma_no_acceptada", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
            elif tag in ["260"]:   
                registre_json.setdefault("empreu", []).append(etiqueta_llegible(etiqueta["subcamps"], "ai"))
            elif tag in ["360"]:
                registre_json.setdefault("tambe", []).append(etiqueta_llegible(etiqueta["subcamps"], "ai"))
            elif tag in ["680"]:
                registre_json.setdefault("abast", []).append(etiqueta_llegible(etiqueta["subcamps"], "ai"))
            elif tag in ["670"]:
                registre_json.setdefault("contexte", []).append(etiqueta_llegible(etiqueta["subcamps"], "b"))
            elif tag.startswith("5"):
                if es_generic(etiqueta["subcamps"]):
                    registre_json.setdefault("generic", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
                else:
                    registre_json.setdefault("relacionats", []).append(etiqueta_llegible(etiqueta["subcamps"], "abcdefghijklmnopqrstuvxyz"))
        
                
    return registre_json
    
def etiqueta_llegible(subcamps, subcamps_acceptats):
    """
    Funció per convertir els subcamps d'una etiqueta a un format més llegible.
    """
    valors_valids = []
    for codi, valors in subcamps.items():
        if codi in subcamps_acceptats:
            for valor in valors:
                if valor == "wnnea" or valor == "wnne" or valor == "g":
                    continue
                if codi in ["v", "x", "y", "z"]:
                    valor = "--" + valor
                else:
                    valor = " " + valor
                valors_valids.append(valor)
    return "".join(valors_valids).strip()
    
def es_generic(subcamps):
    """
    Funció per determinar si una etiqueta és genèrica o no.
    Per això mirem si existeix $wg
    """
    # Aquí podríem implementar la lògica per determinar si una etiqueta és genèrica o no
    for codi, valors in subcamps.items():
        if codi == "w":
            return True    
    return False

def obtenir_titols(encapcalament):
    """
    Funció per obtenir els títols d'un registre a partir de l'encapçalament.
    """
    url = "https://api-eu.hosted.exlibrisgroup.com/primo/v1/search"

    params = {
        "vid": "34CSUC_BC:VU1",
        "tab": "Everything",
        "scope": "MyInst_and_CI",
        "q": f"sub,exact,{encapcalament}",
        "newspapersActive": "true",
        "pcAvailability": "true",
        "lang": "ca_ES",
        "offset": 0,
        "limit": 10,
        "sort": "rank",
        "getMore": 0,
        "conVoc": "true",
        "inst": "34CSUC_BC",
        "skipDelivery": "true",
        "disableSplitFacets": "true",
        "apikey": "l8xx33afaa22fa5d4329a0c50eb48d30b20a"
    }
    titols = []
    try:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        dades = resposta.json()
        
        for document in dades.get("docs", []):
            titol = document["pnx"]["display"]["title"][0]
            titols.append(titol)
    except Exception as e:
        print(f"Error obtenint títols per {encapcalament}: {e}")
    return titols
    