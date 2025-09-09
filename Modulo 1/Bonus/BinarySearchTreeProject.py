# Se inicializa la clase Nodo
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

# Se inicializa la clase BST (Binary Search Tree o Árbol Binario de Búsqueda)
class BST:
    def __init__(self):
        self.raiz = None

    # Se crea el metodo para insertar nodos
    def Insert(self, valor):
        if self.raiz is None:
            self.raiz = Nodo(valor)
        else:
            self.Insert_recursivo(self.raiz, valor)

    def Insert_recursivo(self, nodo_actual, valor):
        if valor < nodo_actual.valor:
            if nodo_actual.izquierda is None:
                nodo_actual.izquierda = Nodo(valor)
            else:
                self.Insert_recursivo(nodo_actual.izquierda, valor)
        else:
            if nodo_actual.derecha is None:
                nodo_actual.derecha = Nodo(valor)
            else:
                self.Insert_recursivo(nodo_actual.derecha, valor)

    # Se crea el metodo para imprimir el árbol
    def PrintTree(self):
        if not self.raiz:
            return

        niveles = self.Get_niveles([self.raiz])
        ancho = 2 ** len(niveles)  # se calcula el ancho para el nivel más profundo

        for i, nivel in enumerate(niveles):
            espacio = " " * (2 ** (len(niveles) - i - 1))
            linea = ""
            for nodo in nivel:
                if nodo is None:
                    linea += espacio + " " + espacio
                else:
                    linea += espacio + str(nodo.valor) + espacio
            print(linea)

    def Get_niveles(self, nodos):
        """Devuelve una lista de niveles con nodos y Nones donde no hay hijos."""
        niveles = []
        while any(n is not None for n in nodos):
            niveles.append(nodos)
            siguiente_nivel = []
            for nodo in nodos:
                if nodo is None:
                    siguiente_nivel.extend([None, None])
                else:
                    siguiente_nivel.append(nodo.izquierda)
                    siguiente_nivel.append(nodo.derecha)
            nodos = siguiente_nivel
        return niveles
    
# ---------------------
# Implementación
# ---------------------
arbol = BST()

# Pedir nodo raíz primero
raiz = int(input("Ingrese el número raíz del árbol: "))
arbol.Insert(raiz)

# Insertar más números
while True:
    numero = input("Ingrese un número para el árbol (o 'fin' para terminar): ")
    if numero.lower() == 'fin':
        break
    if numero.isdigit():
        arbol.Insert(int(numero))
    else:
        print("Ingrese un número válido.")

# Imprimir árbol
print("\nÁrbol Binario de Búsqueda:")
arbol.PrintTree()
