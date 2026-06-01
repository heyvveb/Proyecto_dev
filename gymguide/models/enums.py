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
    Resistencia = "Resistencia"

class TipoSuplementoEnum(str, Enum):
    Proteina = "Proteina"
    Creatina = "Creatina"
    Pre_Entreno = "Pre-Entreno"
    Amino_acidos = "Amino acidos"
    Vitaminas = "Vitaminas"
    Fat_burner = "Fat burner"

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