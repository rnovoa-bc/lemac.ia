#!/usr/bin/python3

import re
import sys

def processRecord(conn, rec):
    leader = rec[0 : 24]
    endDirPosition = rec.find("\x1e", 24)
    directory = rec[24 : endDirPosition]
    data = rec[endDirPosition + 1 : ]
    recType = 1
    cur = conn.cursor()
    cur.execute("insert into registres (capsalera) values (%s)", (leader, ))
    cur.execute("select lastval()")
    recId = cur.fetchone()[0]
    for i in range(1, int(len(directory) / 12)):
        field = directory[(i - 1) * 12 : (i - 1) * 12 + 3]
        if field == "260":
            recType = 2
    fields = data.split("\x1e")[:-1]
    i = 1
    for fieldContent in fields:
        field = directory[(i - 1) * 12 : (i - 1) * 12 + 3]
        try:
            fieldNumber = int(directory[(i - 1) * 12 : (i - 1) * 12 + 3])
        except:
            print(f"Error interpretnant el camp: {directory[(i - 1) * 12 : (i - 1) * 12 + 3]}, {fieldContent}")
            continue
        generic = False

        if fieldNumber > 9:
            if len(fieldContent) > 3:
                ind1 = fieldContent[0]
                ind2 = fieldContent[1]
                fieldContent = fieldContent[2:]
                fieldHuman = re.sub(r"(\x1fv|\x1fx|\x1fy|\x1fz)", "--", fieldContent)
                fieldHuman = re.sub(r"^\x1fwnnea", "", fieldHuman)
                fieldHuman = re.sub(r"^\x1fwnne", "", fieldHuman)
                
                fieldHuman = re.sub(r"\x1f.", " ", fieldHuman).strip()
                generic = True if fieldNumber >= 500 and fieldNumber < 600 and fieldHuman.startswith("g") else False
                fieldHuman = re.sub(r"^g", "", fieldHuman).strip()

                subfields = fieldContent.split("\x1f")
                # entrades per l'index
                
                fieldIndex = re.sub(r"[.,/#!$%^&*;:{}=+\-_`´'\"~()]", " ", fieldHuman)
                
                fieldIndex = re.sub(r"\s+", " ", fieldIndex).strip()
                if   fieldNumber in [100, 110, 111, 130, 150, 151, 155]:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, recType))
                elif fieldNumber in [180]:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 4))
                elif fieldNumber in [185]:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 6))
                elif fieldNumber in [400, 410, 411, 430, 450, 451, 455] and ind1 != "9" and fieldContent.find("\x1f5") == -1:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 3))
                elif fieldNumber == 480 and ind1 != "9" and fieldContent.find("\x1f5") == -1:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 5))
                elif fieldNumber == 485 and ind1 != "9" and fieldContent.find("\x1f5") == -1:
                    cur.execute("insert into index_tmp (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 7))
                elif fieldNumber in [700, 710, 711, 730, 750, 751, 755]:
                    cur.execute("insert into index_tmp_en (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, recType))
                elif fieldNumber in [780]:
                    cur.execute("insert into index_tmp_en (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 4))
                elif fieldNumber in [785]:
                    cur.execute("insert into index_tmp_en (entrada, encapsalament, id_registre, etiqueta, tipus) values(%s, %s, %s, %s, %s)", (fieldIndex, fieldHuman, recId, field, 6))
                # guardem etiquetes i subcamps
                cur.execute("insert into etiquetes (id_registre, etiqueta, ind1, ind2, contingut, generic) values (%s, %s, %s, %s, %s, %s)", \
                    (recId, field, ind1, ind2, fieldHuman, generic))
                cur.execute("select lastval()")
                fieldId = cur.fetchone()[0]
                subfieldCounter = 1
                for subfield in subfields:
                    if len(subfield) >= 2:
                        cur.execute("insert into subcamps (id_etiqueta, ordre, codi, contingut, id_registre, etiqueta) values (%s, %s, %s, %s, %s, %s)", \
                            (fieldId, subfieldCounter, subfield[0], subfield[1:], recId, field))
                        subfieldCounter += 1
        
        else:
            cur.execute("insert into etiquetes (id_registre, etiqueta, contingut, generic) values (%s, %s, %s, %s)", \
                    (recId, field, fieldContent, generic))
            if fieldNumber == 1:
                cur.execute("update registres set id_bc = %s where id = %s", (fieldContent, recId))
        i += 1
    conn.commit()
    cur.close()

def deDup(conn):
    print("Treinet duplicats")
    try:
        cur = conn.cursor()
        cur.execute(
            """
                select duplicats.id_registre from etiquetes duplicats
                inner join (
                    select contingut,etiqueta, min(id_registre) as min_id
                    from etiquetes
                    where etiqueta in ('100','110','111','130','150','151','155')
                    group by contingut,etiqueta
                    having count(*) > 1
                ) valides
                on valides.contingut=duplicats.contingut and valides.etiqueta=duplicats.etiqueta
                and valides.min_id <> duplicats.id_registre order by duplicats.contingut
            """
        )
        for recId in cur.fetchall():
            cur.execute("delete from registres where id=%s", recId)
            cur.execute("delete from index_tmp where id_registre=%s", recId)
            cur.execute("delete from index_tmp_en where id_registre=%s", recId)
        cur.close()
    except Exception as err:
        print(format(err))
        return False
    
    return True

