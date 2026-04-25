from enum import Enum

class CategoriaEnum(str, Enum):
    bodybuilding = "bodybuilding"
    fitness = "fitness"
    powerlifting = "powerlifting"
    crossfit = "crossfit"
    yoga = "yoga"

class LevelEnum(str, Enum):
    Principiante = "Principiante"
    Intermedio = "Intermedio"
    Avanzado = "Avanzado"

class ObjectiveEnum(str, Enum):
    Ganancia_Muscular = "Ganancia Muscular"
    Perdida_de_grasa = "Perdida de grasa"
    Fuerza = "Fuerza"
    Resitencia = "Resitencia"

class TipoSuplementoEnum(str, Enum):
    Proteina = "Proteina"
    Creatina = "Creatina"
    Pre_Entreno = "Pre-Entreno"
    Amino_acidos = "Amino acidos"
    Vitaminas = "Vitaminas"
    Fat_burner = "Fat burner"