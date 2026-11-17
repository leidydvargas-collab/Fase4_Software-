# Fase 4 Software — Sistema de gestión de clientes, servicios y reservas-
## Información académica
- Universidad: Universidad Nacional Abierta ya Distancia — UNAD.
- Programa: Ingeniería de Sistemas
- Curso: Programación
Código del curso: 213023
Grupo: 654
Actividad: Fase 4 — Componente práctico
Estudiante: Leidy Vargas
## Descripción
Este proyecto desarrolla una aplicación en Python diseñada para gestionar la operación comercial de Software FJ mediante un modelo en memoria sin dependencia de bases de datos externas. Sus capacidades principales incluyen:
- Gestión de Entidades y Servicios: Registro de clientes y administración polimórfica de reservas de salas, alquiler de equipos y asesorías especializadas.
- Lógica de Negocio y Tarifación: Cálculo monetario preciso (mediante Decimal), soporte para parámetros opcionales y control de transiciones de estado en las reservas.
- Robustez y Manejo de Errores: Implementación de principios de Programación Orientada a Objetos (POO) y jerarquías de excepciones personalizadas para validar datos de entrada y evitar interrupciones abruptas ante fallos esperados.
## Diseño de arquitectura 
Las clases y funciones no se mezclan en un archivo gigante. Las entidades se ubican en modelos.py; los servicios, en servicios.py; las reservas, en reservas.py; el gestor y las listas, en gestor.py; las validaciones y el logger, en utilidades.py; las excepciones, en excepciones.py; el escenario ejecutable, en app.py; y las pruebas, en pruebas.py. Esto facilita que cinco integrantes trabajen por módulos sin reemplazarse mutuamente los cambios.
|Archivo|Responsabilidad|Decisión que justifica su existencia|
modelos.py	Entidad y Cliente	Separar modelos fundamentales y datos personales.
servicios.py	Tres subtipos de Servicio	Centralizar herencia, polimorfismo y costos.
reservas.py	Reserva y estados	Una sola fuente para las reglas del ciclo de vida.
gestor.py	Listas y disponibilidad	Separar las reglas de coordinación de los objetos.
excepciones.py	Errores específicos	Evitar mensajes ambiguos y manejo genérico innecesario.
utilidades.py	Validación y archivo log	No repetir reglas de formato y conversión.
app.py	21 operaciones	Hacer reproducible la demostración del anexo.
pruebas.py	15 pruebas unitarias	Comprobar resultados sin revisión manual constante.
