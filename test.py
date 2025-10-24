class Persona:
    raza = "Humano"

    def __init__(self, nombre, edad):

        self.nombre = nombre
        self.edad = edad
        

    @classmethod
    def change_raza(cls, raza):
        cls.raza = raza

    @classmethod
    def create_raza(cls, nombre, edad):
        return cls(nombre, edad)


persona1 = Persona("jota", 46)
persona2 = Persona("ana", 44)
print(f"nombre: {persona1.nombre} raza: {persona1.raza} edad: {persona1.edad}")
print(f"nombre: {persona2.nombre} raza: {persona2.raza} edad: {persona2.edad}")


persona3 = Persona.create_raza("jotita", 17)
print(f"nombre: {persona3.nombre} raza: {persona3.raza} edad: {persona3.edad}")

Persona.change_raza("Celestial")
print(f"nombre: {persona3.nombre} raza: {persona3.raza} edad: {persona3.edad}")

#! cambiamos el atributo de clase raza
Persona.change_raza("Humanoide")

print(f"nombre: {persona1.nombre} raza: {persona1.raza} edad: {persona1.edad}")
print(f"nombre: {persona2.nombre} raza: {persona2.raza} edad: {persona2.edad}")
print(f"nombre: {persona3.nombre} raza: {persona3.raza} edad: {persona3.edad}")

persona4 = Persona.create_raza("panchito", 2,)
print(f"nombre: {persona4.nombre} raza: {persona4.raza} edad: {persona4.edad}")
print(persona4.__dict__)