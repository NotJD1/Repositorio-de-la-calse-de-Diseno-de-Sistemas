# ReservaU — PSet 1: Análisis y Diseño

Plataforma de reservas de espacios universitarios (canchas deportivas). Este PSet cubre el ciclo completo: conversación con stakeholders → requerimientos → modelo de dominio → casos de uso → código → simulación → validación.

## Contexto

- **Estudiantes** pueden reservar canchas deportivas disponibles para actividades individuales o informales.
- **Capitanes** de equipos oficiales pueden hacer lo mismo que un estudiante, pero tienen **prioridad de reserva antes de las 6:00 p.m.** (pueden desalojar una reserva de estudiante en conflicto).
- Si un estudiante o capitán **cancela con menos de 2 horas de anticipación** al inicio de su reserva, el sistema la registra automáticamente como **No-Show** en vez de una cancelación regular.
- El **Administrador** gestiona el estado de las canchas y resuelve conflictos de reserva (cancelar o modificar una reserva en disputa).

## Estructura del proyecto

```
psets/pset-01/
├── README.md
├── Requerimientos.docx
├── Diagrama_de_Dominio.docx
├── Casos_de_Uso.docx
├── Diagrama_de_Flujo.docx
└── implementacion/
    ├── dominio.py
    ├── simulacion.py
    └── Dockerfile
```

## Modelo de dominio (resumen)

- `Usuario` (base): `nombre`, `contrasena`, `id_usuario`, `comportamiento_prioridad`.
- `Estudiante`, `Capitan`, `Administrador`: heredan de `Usuario`.
- `ComportamientoPrioridad` (estrategia): `ConPrioridad` (aplica antes de las 18:00) y `SinPrioridad` (nunca aplica) — cada usuario compone su propio comportamiento en vez de decidirlo con un `if`.
- `Cancha`: estado, disponibilidad, `lista_reservas`; valida disponibilidad y agrega/cancela reservas aplicando la regla de prioridad.
- `Reserva`: fecha, horario, estado (`Activa` / `Cancelada` / `No-Show`); `cancelar_reserva()` aplica la regla de las 2 horas.

## Requisitos

- Python 3.12+, o
- Docker

## Ejecutar con Python

```bash
cd implementacion
python simulacion.py
```

## Ejecutar con Docker

```bash
cd implementacion
docker build -t reservau .
docker run reservau
```

El contenedor ejecuta `simulacion.py` de inicio a fin sin necesidad de interacción y sin exponer puertos, volúmenes ni réplicas.

## Qué imprime la simulación

`simulacion.py` recorre, en orden, los flujos principales documentados en los casos de uso:

1. Consulta de reservas de una cancha vacía.
2. Creación exitosa de una reserva de estudiante.
3. Rechazo por conflicto de horario entre estudiantes.
4. Rechazo de un estudiante que intenta chocar con la reserva de un capitán.
5. Un capitán desaloja la reserva de un estudiante por regla de prioridad (antes de las 6 p.m.).
6. Cancelación regular de una reserva (con más de 2 horas de anticipación).
7. Cancelación registrada automáticamente como **No-Show** (con menos de 2 horas de anticipación).

## Trazabilidad

Cada requerimiento funcional (`RF-01` a `RF-08`) documentado en `Requerimientos.docx` debe poder rastrearse hasta un caso de uso, una entidad/método del dominio y un paso observable en `simulacion.py`. Ver `Diagrama_de_Dominio.docx` y `Casos_de_Uso.docx` para el detalle de responsabilidades por clase.
