def main():
    print("Sistema d'entrenament de LEMAC.AI")
    while True:
        mostrar_menu()
        opcio = input("Selecciona una opció: ")
        if opcio == "1":
            print("Preparant dades...")
            # Aquí aniria el codi per preparar les dades
        elif opcio == "2":
            print("Entrenant model...")
            # Aquí aniria el codi per entrenar el model
        elif opcio == "3":
            print("Avaluant model...")
            # Aquí aniria el codi per avaluar el model
        elif opcio == "4":
            print("Guardant model...")
            # Aquí aniria el codi per guardar el model
        elif opcio == "5":
            print("Sortint del programa. Fins aviat!")
            break
        else:
            print("Opció no vàlida. Si us plau, selecciona una opció del 1 al 5.")

def mostrar_menu():
    print("\n" + "-" * 30)
    print("MENÚ PRINCIPAL")
    print("1. Preparar dades")
    print("2. Entrenar model")
    print("3. Avaluar model")
    print("4. Guardar model")
    print("5. Sortir")

if __name__ == "__main__":    main()