# Software FJ · Sistema de clientes, servicios y reservas

Proyecto de simulación en Python para la Fase 4 de Programación (213023), UNAD.
Requiere Python 3.9 o posterior y utiliza únicamente la biblioteca estándar.

## Ejecutar en Windows

1. Extraiga el ZIP. Abra la carpeta Software-FJ que contiene main.py.
2. Haga clic en la barra de dirección del Explorador, escriba cmd y pulse Enter.
3. Ejecute py main.py (o python main.py). El programa ejecuta 22 casos en orden.
4. Compruebe que aparezca «22/22 simulaciones verificadas.» y abra sistema.log.
   Cada nueva ejecución añade una sesión al final del archivo. Los errores de prueba
   tienen nivel ERROR y se consideran correctos cuando coinciden con el tipo esperado.

## Organización

- modelo.py define la clase abstracta Entidad, Cliente con datos encapsulados, la clase abstracta Servicio, sus tres especializaciones, Reserva, Sistema y las excepciones.
- main.py configura el registro, ejecuta las simulaciones y comprueba sus resultados.
- sistema.log conserva la evidencia de las operaciones ejecutadas y sus errores.

## Reglas de la simulación

Los registros se conservan en listas durante la ejecución. Cada servicio representa
un recurso o lote indivisible; una reserva confirmada lo ocupa hasta que se cancela
o se procesa. La duración se mide en horas. El costo en pesos colombianos se calcula
por hora para salas, por hora y unidad para equipos, y por hora más un cargo fijo de
preparación para asesorías. Los porcentajes son parámetros de ejemplo. Primero se
aplica el descuento y luego el impuesto. El método calcular_costo admite ambas
opciones mediante argumentos opcionales y delega el subtotal al servicio concreto.

## Qué observar

El caso 7 conserva la excepción de conversión original mediante raise ... from.
Los casos 11 a 15 muestran ocupación, rechazo, liberación y nueva confirmación.
Los casos 16 y 17 comprueban que un cálculo inválido deja la reserva disponible
para reintentar su procesamiento. El caso 22 comprueba el estado final de las listas.
