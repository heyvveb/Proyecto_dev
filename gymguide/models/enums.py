from enum import Enum
#Enum de las categorias de influencer
class CategoriaEnum(str, Enum):
    bodybuilding = "bodybuilding"
    fitness = "fitness"
    powerlifting = "powerlifting"
    crossfit = "crossfit"
    yoga = "yoga"
    def __str__(self):
        return self.value
#Enum para los niveles de las rutinas
class LevelEnum(str, Enum):
    Principiante = "Principiante"
    Intermedio = "Intermedio"
    Avanzado = "Avanzado"
    def __str__(self):
        return self.value
#Enum para el objetivo de las rutinas
class ObjectiveEnum(str, Enum):
    Ganancia_Muscular = "Ganancia Muscular"
    Perdida_de_grasa = "Perdida de grasa"
    Fuerza = "Fuerza"
    Resistencia = "Resistencia"
    def __str__(self):
        return self.value
#Enum de los tipos de suplementos
class TipoSuplementoEnum(str, Enum):
    Proteina = "Proteina"
    Creatina = "Creatina"
    Pre_Entreno = "Pre-Entreno"
    Amino_acidos = "Amino acidos"
    Vitaminas = "Vitaminas"
    Fat_burner = "Fat burner"
    def __str__(self):
        return self.value
#Enums de los grupos musculares de los ejercicios
class GrupoMuscularEnum(str, Enum):
    Pecho = "Pecho"
    Espalda = "Espalda"
    Hombros = "Hombros"
    Biceps = "Biceps"
    Triceps = "Triceps"
    Piernas = "Piernas"
    Gluteos = "Gluteos"
    Abdominales = "Abdominales"
    Cardiovascular = "Cardiovascular"
    def __str__(self):
        return self.value