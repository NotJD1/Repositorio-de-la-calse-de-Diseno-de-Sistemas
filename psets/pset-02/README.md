# ReservaU v2: PSet 2, Patrones de Diseño

**Autor:** Juan David Espinosa
**Materia:** Diseño de Sistemas

## Descripción

ReservaU v2 es el sistema de reservas de canchas deportivas de dos sedes (Campus Norte y Campus Sur). Permite reservar, reservar de forma recurrente, cancelar y bloquear canchas, aplicando patrones de diseño y control de concurrencia.

## Estructura del proyecto

```
psets/pset-02/
├── implementacion/
│   ├── reservau.py       # Todas las clases y patrones
│   ├── simulacion.py     # Simulación con 7 escenarios
│   └── Dockerfile
└── entregables/          # Diagramas (casos de uso, dominio, flujo,
                          # robustez, secuencia, actividad y estados)
```

## Reglas de negocio principales

- **Sede Norte:** abre de 06:00 a 22:00 y notifica por correo institucional.
- **Sede Sur:** abre de 07:00 a 23:00 y notifica por mensaje de texto.
- **Prioridad:** las reservas de equipo (capitanes) con hora de inicio hasta las 18:00 tienen prioridad y pueden desplazar a una reserva sin prioridad en la misma cancha, fecha y hora.
- **No-show:** cancelar con menos de 2 horas (estudiantes) o 24 horas (capitanes) de anticipación cuenta como no-show.
- **Suspensión:** 3 no-shows en el mismo mes calendario suspenden al usuario 7 días.
- **Administrador:** puede anular reservas y nunca genera penalización.
- **Reserva recurrente:** solo capitanes, de 2 a 8 semanas, todo o nada. Si una semana falla, no se guarda ninguna y se indica la semana en conflicto.

## Patrones aplicados

|      Patrón      | Requerimiento que lo justifica | Problema que resuelve | Clases y métodos |
|------------------|--------------------------------|-----------------------|------------------|
|  **Factory Method** | RF-2 (reserva de estudiante y de capitán) | Sin él, cada lugar que crea una reserva repetiría un if según el tipo de usuario | `ReservasFactory.crear_reserva` |
| **Abstract Factory** | RF-21 (horario y canal de notificación por sede) | Sin él habría if sede == Norte/Sur al validar y al notificar, y se podría mezclar el validador de una sede con el notificador de otra | `SedeFactory`, `SedeNorteFactory`, `SedeSurFactory`: `crear_validador`, `crear_notificador`, `horario_valido`, `enviar_notificacion` |
|      **Builder**     | RF-9 (reserva recurrente de 2 a 8 semanas con equipo y notas) | Evita un constructor con muchos parámetros opcionales y concentra las validaciones en `construir()` | `ReservaRecurrenteBuilder`: `add_semanas`, `add_equipo_prestado`, `add_notas`, `construir` |
|     **Prototype**    | RF-9 (bloqueo definido una vez y replicado en varias canchas y fechas) | Sin él habría que armar el bloqueo a mano en cada cancha y fecha | `Bloqueo.clonar`, `Administrador.aplicar_bloqueo` |
|     **Singleton**    | RF-25 (valores de las reglas en un único lugar) | Evita números repartidos por el código | `ValoresImportantes`, `get_valores` |
|     **Strategy**     | RF-5 (prioridad hasta las 18:00, no-show de 2 y 24 horas, el administrador no penaliza) | Sin él, `Reserva` tendría if por tipo de usuario para prioridad y no-show | `EstrategiaPrioridad` (`ConPrioridad`, `SinPrioridad`), `EstrategiaNoshow` (`NoShowRegular`, `NoShowCapitan`, `AnulacionAdministrador`): `noshow` |
|      **Facade**       | RNF-6(flujos de reservar, cancelar y bloquear) | Sin él, quien llame tendría que conocer la fábrica, el validador, la cancha, el candado y el notificador | `ReservaFacade`: `reservar_cancha`, `reservar_recurrente`, `cancelar_reserva`, `bloquear_cancha` |
| **Concurrencia (bloqueo pesimista)** | RNF-1 (no puede haber dos confirmaciones para la misma cancha y hora) | Dos usuarios verifican a la vez, ambos ven la cancha libre y ambos reservan | `ReservaFacade.candado` (`threading.Lock`) con `with candado:` en `reservar_cancha`, `reservar_recurrente`, `cancelar_reserva` y `bloquear_cancha` |

## Decisiones de diseño

### Prototype: copy vs deepcopy

`Bloqueo` es la plantilla (motivo, hora de inicio, hora de fin y equipo). `clonar(cancha, fecha)` usa `deepcopy`. Con una copia superficial (`copy`), el clon y la plantilla compartirían la misma lista de `equipo`. Si le agrego "chalecos" al bloqueo de una cancha, la plantilla cambiaría y también los bloqueos de las demás canchas, aunque no los necesiten. Con `deepcopy` cada cancha tiene su propia lista de equipo opcional. Esto se comprueba en el escenario 6 de la simulación.

### Singleton: ventaja y costo

`ValoresImportantes` concentra en un solo lugar la hora límite de prioridad (18:00), las ventanas de no-show (120 y 1440 minutos), el máximo de 3 vetos y los 7 días de suspensión. Las clases los leen con `get_valores()`, sin tener que buscar números sueltos en el código, y si algo cambia se modifica en un solo sitio.

El costo es que es estado global: todo el sistema comparte los mismos valores y las clases dependen de él sin que se vea en sus constructores. Por eso, probar con otros valores o tener valores distintos por sede obligaría a modificar la instancia única.

### Concurrencia: bloqueo pesimista

`agregar_reserva` se ejecuta dentro de un `with candado:` en el Facade. Quien entra primero se queda con la franja; el otro espera y, al entrar, ve la cancha ocupada y recibe un rechazo definitivo. Elegí bloqueo pesimista porque verificar y guardar ocurren de forma atómica, así nunca hay dos reservas en la misma franja. Con bloqueo optimista, los dos usuarios podrían creer que la reserva pasó y uno perdería después. Prefiero un rechazo claro desde el inicio, para que el usuario considere otras opciones en vez de darle falsas esperanzas. El escenario 7 lo prueba con dos hilos al mismo tiempo: queda exactamente 1 reserva confirmada.

### Un solo candado global

Uso un solo candado para todo el sistema. Es simple, no hay que repetir código de bloqueo por cancha y se evita tener que definir en qué orden se adquieren los candados (por ejemplo, Norte antes que Sur) cuando una operación toca varias canchas, como bloquear en varias sedes. El costo es que reservas de canchas distintas también se esperan entre sí. Para el tamaño de este proyecto, las operaciones son cortas y es aceptable.

### Reloj simulado

El sistema nunca usa la fecha ni la hora actual. Cada operación recibe un `momento` desde afuera. Así la simulación da siempre el mismo resultado sin importar cuándo se ejecute.

## Limitaciones conocidas

- La duración de cada reserva es fija (1 hora). No se maneja hora de fin elegida por el usuario.
- La reasignación automática de cancha cuando una reserva es anulada no está implementada.
- La prioridad solo desplaza reservas sin prioridad que coincidan en cancha, fecha y hora de inicio.
- El administrador solo cancela y bloquea; no puede hacer reservas.

## Cómo ejecutar

Requiere Python 3.12 y no usa librerías externas.

**Local** (desde la carpeta `psets/pset-02/implementacion`):

```
python simulacion.py
```

**Con Docker** (desde la misma carpeta):

```
docker build -t reservau-v2 .
docker run reservau-v2
```

## Simulación

`simulacion.py` ejecuta 7 escenarios:

1. Una reserva en cada sede, validada y notificada según su sede.
2. Reserva rechazada por estar fuera del horario de la sede.
3. Reserva recurrente exitosa y otra rechazada por conflicto en la semana 2.
4. Tres cancelaciones con resultados distintos: a tiempo, no-show de capitán y anulación del administrador.
5. Tres no-shows en el mismo mes, suspensión de 7 días y reserva permitida al terminar.
6. Bloqueo clonado en dos canchas, con una reserva existente anulada.
7. Dos hilos intentan reservar la misma cancha y franja: solo uno la obtiene.