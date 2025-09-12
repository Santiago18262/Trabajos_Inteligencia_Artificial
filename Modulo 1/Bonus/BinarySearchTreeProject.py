# Se inicializa la clase Nodo
class Nodo:
    def __init__(self, valor):
        self.valor = valor    # Cada nodo se almacena en un valor
        self.izquierda = None # Cada nodo tiene un hijo izquierdo
        self.derecha = None # Cada nodo tiene un hijo derecho

# Se inicializa la clase BST (Binary Search Tree o Árbol Binario de Búsqueda)
class BST:
    def __init__(self):
        self.raiz = None # El árbol comienza sin nodos

    # Se crea el metodo para insertar nodos
    def insert(self, valor):
        if self.raiz is None:     # Si el árbol está vacío, el nuevo nodo se convierte en la raíz
            self.raiz = Nodo(valor)
        else:
            self.insert_recursivo(self.raiz, valor) # Si ya existe la raíz, se llama al método recursivo para encontrar la posición correcta

    def insert_recursivo(self, nodo_actual, valor):
        if valor < nodo_actual.valor: # Si el valor es menor, se va a la izquierda
            if nodo_actual.izquierda is None:
                nodo_actual.izquierda = Nodo(valor)
            else:
                self.insert_recursivo(nodo_actual.izquierda, valor) # Llamada recursiva a la izquierda
        else:
            if nodo_actual.derecha is None: # Si el valor es mayor o igual, se va a la derecha
                nodo_actual.derecha = Nodo(valor)
            else:
                self.insert_recursivo(nodo_actual.derecha, valor) # Llamada recursiva a la derecha

    # Se crea el metodo para imprimir el árbol
    def printTree(self):
        if not self.raiz:
            return

        niveles = self.get_niveles([self.raiz]) # obtiene los niveles del árbol
        ancho = 2 ** len(niveles)  # se calcula el ancho para el nivel más profundo

        for i, nivel in enumerate(niveles): # Recorre cada nivel
            espacio = " " * (2 ** (len(niveles) - i - 1)) # Calcula el espacio para centrar los nodos
            linea = ""
            for nodo in nivel: # Recorre cada nodo en el nivel
                if nodo is None:
                    linea += espacio + " " + espacio # Si el nodo es None, se imprime un espacio
                else:
                    linea += espacio + str(nodo.valor) + espacio # Si el nodo existe, se imprime su valor y su espacio
            print(linea)

    def get_niveles(self, nodos):
        """Devuelve una lista de niveles con nodos y Nones donde no hay hijos."""
        niveles = []
        while any(n is not None for n in nodos): # Mientras haya nodos no vacios en el nivel
            niveles.append(nodos)
            siguiente_nivel = []
            for nodo in nodos: # Recorre cada nodo en el nivel actual
                if nodo is None: # Si el nodo es None, se agregan dos Nones para sus hijos
                    siguiente_nivel.extend([None, None])
                else: #Si el nodo existe, se agregan sus hijos
                    siguiente_nivel.append(nodo.izquierda)
                    siguiente_nivel.append(nodo.derecha)
            nodos = siguiente_nivel # Se actualiza la lista de nodos al siguiente nivel
        return niveles
    
# ---------------------
# Implementación
# ---------------------
arbol = BST()

# Pedir nodo raíz primero
raiz = int(input("Ingrese el número raíz del árbol: "))
arbol.insert(raiz)

# insertar más números
while True:
    numero = input("Ingrese un número para el árbol (o 'fin' para terminar): ")
    if numero.lower() == 'fin':
        break
    if numero.isdigit():
        arbol.insert(int(numero))
    else:
        print("Ingrese un número válido.")

# Imprimir árbol
print("\nÁrbol Binario de Búsqueda:")
arbol.printTree()
