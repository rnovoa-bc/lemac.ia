import json

def prepara():
    """
    Legirem un fitxer ISO2709 amb les dades de la LEMAC
    i el convertirem a un format JSON que serà més fàcil d'utilitzar per entrenar el model.
    """

    compatador = 0
    for registre in llegir_registres_iso():
        registre_processat = analitza_registre(registre)
        imprimir_registre(registre_processat)
        compatador += 1
        if compatador >= 10:
            break
    

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
            parts = tros.split(b"\x1d")  # Separador de registres en ISO2709
            for registre in parts[:-1]:
                yield registre
        
            buffer = parts[-1]

    if buffer:
        yield buffer

def analitza_registre(registre):
    """
    Funció per processar un registre ISO2709 i convertir-lo a un format diccionari.
    """
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
            for subcamp in camp_dades.split(b"\x1f")[1:]:  # Els subcamps comencen amb un separador de subcamp (0x1f)
                if subcamp:
                    codi = subcamp[:1].decode("utf-8")
                    valor = subcamp[1:].decode("utf-8")
                    subcamps.setdefault(codi, []).append(valor)
            etiqueta = {"indicadors": indicadors, "subcamps": subcamps}
            etiquetes.setdefault(tag, []).append(etiqueta)

    return { "capacalera": capacalera, "etiquetes": etiquetes }

def imprimir_registre(registre):
    """
    Funció per imprimir un registre en pantalla per depurar analiza_registre.
    """
    print("#"*80)
    print(f"Capçalera: {registre["capacalera"]}")
    for tag, contingut in registre["etiquetes"].items():
        if isinstance(contingut, dict):
            print(f"Etiqueta: {tag}; Indicadors: {field['indicators'].replace(" ", "□")}")
            for codi, valors in field["subcamps"].items():
                for valor in valors:
                    print(f"  ${codi} {valor}")
        else:
            print(f"Control {tag}: {contingut}")
    

    