---
titulo: "Plataforma Inteligente de Atención de Emergencias Vehiculares - Segundo Parcial"
tipo_documento: "Conversión AI-optimized de PDF a Markdown"
fuente: "2do Parcial G22.pdf"
materia: "Sistemas de Información II - INF412"
universidad: "Universidad Autónoma Gabriel René Moreno"
grupo: 22
integrantes:
  - "Melgar Gushi Diego"
  - "Ortiz Montero Luis Enrique"
semestre: "I/2026"
continuacion_de: "Primer Parcial - ciclos 1, 2 y 3"
ciclos_documentados:
  - "Ciclo 4"
  - "Ciclo 5"
stack_principal:
  backend: "Python + FastAPI"
  frontend_web: "Angular"
  frontend_movil: "Flutter / Dart"
  base_datos: "PostgreSQL + PostGIS"
  realtime: "WebSockets"
  offline: "Persistencia local + sincronización automática"
  arquitectura: "SaaS multi-tenant"
  analitica: "Dashboards operacionales + KPIs + reportes por tenant"
  pagos: "Pasarela de pagos y penalidades por cancelación"
uso_recomendado: "Contexto para IA, SDD, arquitectura, requisitos, análisis, diseño, implementación, pruebas y refactorización"
fecha_conversion: "2026-07-02"
---

# Plataforma Inteligente de Atención de Emergencias Vehiculares - Segundo Parcial optimizado para IA

> **Objetivo de este Markdown:** convertir el PDF del segundo parcial en una fuente de contexto más eficiente para IA, sin perder información valiosa. Este archivo sintetiza, ordena y normaliza el documento original para que un modelo pueda comprender el alcance de los ciclos 4 y 5, sus casos de uso, arquitectura, paquetes, datos, pruebas, riesgos e inconsistencias técnicas.

> **Relación con el primer parcial:** este documento es la continuación del proyecto. El primer parcial cubría los ciclos 1, 2 y 3: autenticación, roles, clientes, vehículos, talleres, emergencia multimodal, IA, asignación, seguimiento, notificaciones, pagos, reseñas, historial y supervisión. El segundo parcial amplía la plataforma con los ciclos 4 y 5.

---

## 1. Resumen ejecutivo para IA

El segundo parcial evoluciona la **Plataforma Inteligente de Atención de Emergencias Vehiculares** hacia una solución más cercana a operación real. La plataforma mantiene el núcleo definido en el primer parcial - cliente móvil, taller web, backend FastAPI y PostgreSQL -, pero agrega capacidades avanzadas para escalabilidad, disponibilidad, trazabilidad y analítica.

La evolución funcional se concentra en cinco ejes:

1. **Arquitectura SaaS multi-tenant:** permite que múltiples organizaciones o redes de talleres utilicen la misma plataforma, manteniendo separación lógica de datos.
2. **Aislamiento de datos por tenant:** cada usuario, taller, incidente, pago, cotización, métrica o reporte debe pertenecer a un tenant específico y no puede cruzarse con otro.
3. **Modo offline + sincronización:** permite registrar emergencias sin conexión y enviarlas al backend cuando se restablece internet.
4. **Tracking en vivo mediante WebSockets:** permite actualizar ubicación del técnico, estado del servicio y eventos relevantes en tiempo real.
5. **Analítica, cotizaciones, pagos y reportes:** incorpora dashboards con KPIs, cotizaciones por taller, selección de taller, pasarela de pagos, penalidades por cancelación y reportes operacionales por tenant.

El documento aplica metodología **PUDS-UML 2.5+** y contiene captura de requisitos, priorización, detalle de casos de uso, prototipado, modelos de casos de uso, análisis de arquitectura, comunicación, clases, paquetes, diseño de arquitectura, diseño de datos, diagramas de secuencia, navegación, red, estado, tiempo, implementación y pruebas.

---

## 2. Ficha rápida del sistema

| Campo | Detalle |
|---|---|
| Nombre del sistema | Plataforma Inteligente de Atención de Emergencias Vehiculares |
| Materia | Sistemas de Información II - INF412 |
| Segundo parcial | Continuación con ciclos 4 y 5 |
| Dominio | Emergencias vehiculares, asistencia mecánica, geolocalización, IA, SaaS, analítica operacional |
| Metodología | PUDS + UML 2.5+ |
| Backend | Python + FastAPI |
| Web | Angular |
| Móvil | Flutter / Dart |
| Base de datos | PostgreSQL + PostGIS |
| Realtime | WebSockets |
| Offline | Persistencia local, PWA, sincronización automática |
| Analítica | Dashboard operacional, KPIs, reportes, métricas SLA |
| Multi-tenant | Tenants, redes de talleres, aislamiento lógico de datos |
| Pagos | Pasarela de pagos, comprobantes, pagos pendientes, confirmación, penalidades |
| Repositorio | `https://github.com/DiegoMelgar61/Plataforma-Inteligente-de-Atenci-n-de-Emergencias-Vehiculares.git` |
| Software web | `https://plataforma-inteligente-de-atenci-n.vercel.app/map` |

---

## 3. Problema que resuelve esta segunda fase

En la primera fase, la plataforma permitía registrar incidentes, asignar talleres y realizar seguimiento básico. Sin embargo, para funcionar en un entorno real y escalable todavía existían limitaciones:

- Falta de actualización inmediata en tiempo real.
- Dependencia total de conexión estable a internet.
- Falta de registro de emergencias en zonas con baja cobertura.
- Ausencia de dashboards operacionales para supervisar tiempos, cumplimiento, productividad o cancelaciones.
- Diseño inicial orientado a una sola organización.
- Falta de separación de información entre distintas redes de talleres.
- Necesidad de gestionar cotizaciones, selección de talleres, pagos digitales, penalidades y reportes.

La segunda fase convierte el sistema en una plataforma más robusta: **multi-tenant, tolerante a desconexión, con seguimiento en vivo, analítica operacional y flujo económico más completo**.

---

## 4. Objetivo general del segundo parcial

Evolucionar la plataforma inteligente de atención de emergencias vehiculares mediante la implementación de funcionalidades de tiempo real, sincronización offline, analítica operacional y arquitectura SaaS multi-tenant, con el fin de mejorar la eficiencia, trazabilidad, escalabilidad y gestión de los servicios dentro de un entorno más cercano a una operación real.

---

## 5. Objetivos específicos

- Implementar comunicación en tiempo real mediante **WebSockets** para seguimiento y actualización de incidentes.
- Desarrollar funcionamiento **offline** para registrar emergencias sin internet.
- Sincronizar automáticamente emergencias pendientes cuando se restablezca la conexión.
- Incorporar dashboards operacionales con **KPIs** calculados desde datos reales.
- Implementar arquitectura **SaaS multi-tenant** para múltiples organizaciones o redes de talleres.
- Mejorar trazabilidad y monitoreo durante todo el flujo de atención.
- Integrar pagos digitales y cotizaciones.
- Generar reportes operacionales filtrados por tenant.
- Aplicar PUDS y UML 2.5+ durante análisis, diseño, implementación y pruebas.

---

## 6. Alcance del segundo parcial

El sistema contempla:

- Aplicación web.
- Aplicación móvil.
- Backend en FastAPI.
- Base de datos PostgreSQL.
- Comunicación en tiempo real mediante WebSockets.
- Modo offline con sincronización automática.
- Dashboards operacionales con KPIs.
- Arquitectura SaaS multi-tenant.
- Registro y seguimiento de emergencias.
- Asignación de talleres.
- Gestión de cotizaciones.
- Selección de taller por el cliente.
- Visualización de tiempos estimados de reparación.
- Pago mediante pasarela.
- Aislamiento lógico de datos entre tenants.

**Límite del alcance:** el proyecto es funcional y académico. No contempla despliegues productivos masivos ni integraciones bancarias reales en entornos comerciales.

---

## 7. Marco teórico optimizado para IA

### 7.1 Comunicación en tiempo real

La comunicación en tiempo real es el intercambio inmediato de datos entre sistemas conectados. Es clave para que cliente, técnico, taller y backend compartan estados y ubicaciones sin recargar manualmente la aplicación.

#### WebSockets

WebSocket es un protocolo bidireccional sobre una conexión persistente TCP. A diferencia de HTTP tradicional, mantiene una sesión abierta entre cliente y servidor.

Características relevantes:

- Comunicación bidireccional.
- Baja latencia.
- Conexión persistente.
- Transmisión continua.
- Menor sobrecarga que múltiples solicitudes HTTP.

En este proyecto, WebSockets se usa para:

- Tracking GPS del técnico.
- Actualizaciones de estado del incidente.
- Seguimiento en vivo del servicio.
- Notificaciones inmediatas durante la atención.

#### Tracking en tiempo real

El tracking permite monitorear ubicación, estado o movimiento de entidades móviles. En este sistema aplica principalmente al técnico/taller asignado y al estado de la emergencia.

#### Geolocalización

Permite ubicar clientes, incidentes, técnicos y talleres usando GPS, redes móviles, Wi-Fi o servicios de mapas. Es clave para asignación, tracking y mapas de calor.

---

### 7.2 Funcionamiento offline y sincronización

#### Funcionamiento offline

Permite que la aplicación continúe operando parcialmente sin conexión. En este proyecto, el cliente puede registrar una emergencia aunque no tenga internet.

Debe garantizar:

- Persistencia temporal de datos.
- Integridad de información.
- Continuidad funcional.
- Recuperación posterior de sincronización.

#### Sincronización de datos

Proceso mediante el cual los datos guardados localmente se envían al backend central cuando vuelve la conexión.

Debe contemplar:

- Identificadores locales.
- Prevención de duplicados.
- Resolución de conflictos.
- Cambio de estado local de `pendiente` a `sincronizada`.
- Registro correcto en backend y base de datos.

#### Persistencia local

Puede implementarse con:

- SQLite.
- IndexedDB.
- Local Storage.
- Caché de aplicación.

#### PWA y Service Workers

Las Progressive Web Apps permiten funcionamiento offline, instalación, notificaciones push y almacenamiento local. Los Service Workers interceptan solicitudes de red, gestionan caché y habilitan sincronización en segundo plano.

---

### 7.3 Analítica operacional y KPIs

La analítica operacional usa datos del sistema para monitorear desempeño y apoyar decisiones.

En este proyecto aplica a:

- Tiempos promedio de atención.
- Incidentes por tipo.
- Talleres eficientes.
- Zonas con más incidentes.
- Casos cancelados.
- Cumplimiento SLA.
- Pagos registrados.
- Rendimiento por taller o técnico.

#### Dashboard

Interfaz visual con tarjetas, gráficos, tablas y filtros para consultar indicadores.

#### KPIs

Indicadores clave para medir eficiencia, calidad, cumplimiento y productividad.

#### SLA

Acuerdo de nivel de servicio; define tiempos mínimos esperados de respuesta y calidad de atención.

#### Trazabilidad

Registro histórico de eventos: quién hizo qué, cuándo, sobre qué incidente, desde qué rol o tenant.

---

### 7.4 Arquitectura SaaS multi-tenant

#### SaaS

Modelo donde el software se ofrece como servicio accesible por internet. Centraliza infraestructura, mantenimiento y actualizaciones.

#### Multi-tenant

Modelo donde varias organizaciones comparten la misma plataforma, pero cada una opera con datos separados lógicamente.

Cada tenant posee:

- Usuarios propios.
- Talleres propios.
- Técnicos propios.
- Incidentes propios.
- Configuraciones propias.
- Pagos, reportes y métricas propias.

#### Aislamiento de datos

Regla central del segundo parcial: ningún tenant debe ver información de otro. Puede implementarse mediante:

- Filtro lógico por `tenant_id`.
- Restricciones de acceso.
- Esquemas separados.
- Bases de datos independientes.
- Row-Level Security si se usa Supabase/PostgreSQL.

---

## 8. Actores del sistema

| Actor | Rol | Funciones principales |
|---|---|---|
| Cliente / Conductor | Usuario final que solicita auxilio mecánico | Registrarse, registrar vehículos, reportar emergencias, enviar ubicación/fotos/audio, consultar estado, pagar, seleccionar taller, cancelar solicitud |
| Dueño del Taller | Responsable operativo del taller | Registrar taller, gestionar técnicos, ver solicitudes, cotizar, aceptar/rechazar, consultar dashboard y reportes |
| Técnico Mecánico | Operador que presta asistencia física | Recibir orden, actualizar estado, compartir ubicación, ejecutar atención |
| Módulos de IA | Procesamiento inteligente | Transcripción de audio, resúmenes, clasificación, priorización, apoyo a penalidad/métricas si se extiende |
| Administrador del Sistema | Gestión global | Gestionar tenants, roles, usuarios, aislamiento de datos, métricas, reportes, supervisión |
| Sistema | Actor interno | Validar tenant, sincronizar pendientes, establecer WebSockets, registrar historial, calcular KPIs |
| Pasarela de Pago | Servicio externo | Validar transacción, confirmar o rechazar pago |

---

## 9. Casos de uso del segundo parcial - resumen ejecutivo

### 9.1 Ciclo 4

| ID | Caso de uso | Prioridad | Riesgo | Actores | Propósito resumido |
|---|---|---:|---:|---|---|
| CU16 | Administrar tenants y redes de talleres | Crítica | Alto | Administrador | Registrar y administrar organizaciones o redes de talleres bajo modelo SaaS multi-tenant |
| CU17 | Validar aislamiento de datos por tenant | Crítica | Alto | Sistema, Administrador | Garantizar que cada usuario solo acceda a datos de su tenant |
| CU18 | Registrar emergencia en modo offline | Crítica | Alto | Cliente | Permitir registrar emergencias sin internet, guardándolas localmente |
| CU19 | Sincronizar emergencias pendientes | Crítica | Alto | Cliente, Sistema | Enviar al backend emergencias offline cuando vuelve la conexión |
| CU20 | Gestionar tracking en vivo mediante WebSockets | Crítica | Alto | Cliente, Técnico, Taller, Sistema | Transmitir ubicación y estado del incidente en tiempo real |

### 9.2 Ciclo 5

| ID | Caso de uso | Prioridad | Riesgo | Actores | Propósito resumido |
|---|---|---:|---:|---|---|
| CU21 | Gestionar cotizaciones y selección de taller | Crítica | Medio | Cliente, Dueño del Taller | Talleres cotizan; cliente compara y selecciona taller |
| CU22 | Integrar / procesar pago mediante pasarela | Crítica | Alto | Cliente, Sistema, Pasarela | Validar transacción y actualizar estado de pago |
| CU23 | Visualizar dashboard operacional por tenant | Crítica | Medio | Administrador, Dueño del Taller | Mostrar KPIs reales filtrados por tenant |
| CU24 | Gestionar penalidad por cancelación de solicitud | Crítica | Alto | Cliente, Administrador | Aplicar multa cuando se cancela una solicitud avanzada |
| CU25 | Generar reportes operacionales por tenant | Crítica | Medio | Administrador, Dueño del Taller | Generar reportes exportables filtrados por tenant |
| CU26 | Generar cobro de multa por cancelación impulsado por IA | Crítica | Medio | Administrador, Cliente | Generar cobro de multa asociado a cancelación avanzada |
| CU27 | Visualizar mapa de calor de incidentes por zona | Crítica | Medio | Dueño del Taller, Administrador | Visualizar zonas con mayor concentración de incidentes |

> **Nota de consistencia:** CU26 y CU27 aparecen en la tabla de casos de uso y en pruebas, pero no están completamente desarrollados en la sección 3.1.3 de detalle de casos de uso ni en todos los diagramas principales. Para una documentación final, deben normalizarse como parte del Ciclo 5 o moverse a backlog.

---

## 10. Detalle operativo de casos de uso - Ciclo 4

### CU16. Administrar Tenants y Redes de Talleres

- **Propósito:** registrar, modificar y administrar organizaciones o redes de talleres que usarán la plataforma bajo modelo SaaS multi-tenant.
- **Actor principal:** Administrador.
- **Precondición:** administrador SaaS autenticado con permisos globales.
- **Flujo principal:**
  1. Accede al módulo de administración de tenants.
  2. Registra una nueva organización o red de talleres.
  3. Ingresa datos del tenant, estado, responsable y configuración inicial.
  4. Asocia talleres, usuarios e información operativa.
  5. Guarda el tenant en base de datos.
  6. Confirma creación o actualización.
- **Postcondición:** tenant registrado o actualizado y habilitado para operar.
- **Excepciones:** datos incompletos, tenant duplicado, usuario sin permisos, error de registro.
- **Relaciones:** incluye o depende de CU17 para aislamiento.

### CU17. Validar Aislamiento de Datos por Tenant

- **Propósito:** asegurar que usuarios, talleres, incidentes, pagos, cotizaciones y métricas pertenezcan a un solo tenant.
- **Actor principal:** Sistema.
- **Actores:** Sistema, Administrador; visualmente también afecta a Cliente, Técnico y Dueño del Taller.
- **Precondición:** usuario autenticado y asociado a tenant válido.
- **Flujo principal:**
  1. Usuario inicia sesión.
  2. Sistema identifica el tenant del usuario autenticado.
  3. Backend aplica filtro de tenant en consultas.
  4. Sistema recupera solo datos del tenant correspondiente.
  5. Registra operación para trazabilidad.
- **Postcondición:** usuario visualiza solo información de su tenant.
- **Excepciones:** usuario sin tenant, intento de acceso externo, token inválido, error en filtro.
- **Regla crítica:** toda consulta sensible debe incorporar `tenant_id` o equivalente.

### CU18. Registrar Emergencia en Modo Offline

- **Propósito:** permitir que el cliente registre una emergencia sin conexión y la deje pendiente de sincronización.
- **Actor principal:** Cliente.
- **Precondición:** cliente autenticado previamente en app móvil/PWA; ausencia de conexión.
- **Flujo principal:**
  1. Cliente accede a registrar emergencia.
  2. Sistema detecta falta de internet.
  3. Cliente ingresa incidente, ubicación, descripción y evidencias.
  4. Aplicación guarda datos localmente.
  5. Incidente queda como `pendiente de sincronización`.
  6. Sistema informa que aún no fue enviado al servidor.
- **Postcondición:** emergencia almacenada localmente.
- **Excepciones:** error al guardar, datos incompletos, falta de permisos de ubicación, almacenamiento insuficiente.
- **Diseño sugerido:** usar `local_id`, `sync_status`, `created_offline_at`, `retry_count`, `last_sync_error`.

### CU19. Sincronizar Emergencias Pendientes

- **Propósito:** enviar al backend emergencias offline al recuperar conexión, evitando duplicados.
- **Actor principal:** Sistema.
- **Actores:** Cliente, Sistema.
- **Precondición:** existe una emergencia local pendiente y la conexión volvió.
- **Flujo principal:**
  1. App detecta recuperación de conexión.
  2. Consulta emergencias pendientes en almacenamiento local.
  3. Valida identificador local para evitar duplicados.
  4. Envía emergencia al backend.
  5. Backend registra incidente en base de datos.
  6. App actualiza estado local a `sincronizada`.
  7. Usuario recibe confirmación.
- **Postcondición:** emergencia sincronizada y marcada como enviada.
- **Excepciones:** pérdida de conexión, duplicado, falla backend, error al actualizar estado local.
- **Regla crítica:** el backend debe ser idempotente con base en `local_id` + `tenant_id` + `user_id`.

### CU20. Gestionar Tracking en Vivo mediante WebSockets

- **Propósito:** visualizar ubicación del técnico/taller y estado del incidente en tiempo real.
- **Actor principal:** Técnico.
- **Actores:** Cliente, Técnico, Dueño del Taller, Sistema.
- **Precondición:** incidente registrado, aceptado por taller y con técnico asignado.
- **Flujo principal:**
  1. Técnico inicia atención.
  2. App obtiene ubicación actual del técnico.
  3. Sistema establece conexión WebSocket entre cliente, taller y backend.
  4. Técnico envía actualizaciones de ubicación y estado.
  5. Cliente visualiza avance y estado actualizado.
  6. Sistema registra cambios en historial.
- **Postcondición:** ubicación y estado actualizados en tiempo real.
- **Excepciones documentadas:** el PDF indica “credenciales incorrectas o usuario no registrado”.
- **Corrección recomendada:** excepciones más coherentes serían: conexión WebSocket fallida, técnico sin permisos, incidente no asignado, pérdida de GPS, token expirado, intento de suscripción a otro tenant.

---

## 11. Detalle operativo de casos de uso - Ciclo 5

### CU21. Gestionar Cotizaciones y Selección de Taller

- **Propósito:** permitir que talleres generen cotizaciones y que el cliente seleccione el taller según precio, tiempo estimado y disponibilidad.
- **Actor principal:** Cliente.
- **Actores:** Cliente, Dueño del Taller.
- **Precondición:** incidente registrado, clasificado y disponible para talleres del tenant.
- **Flujo principal:**
  1. Cliente registra o consulta emergencia.
  2. Dueño del taller revisa incidente, evidencias y clasificación.
  3. Taller genera cotización con monto estimado.
  4. Cliente visualiza cotizaciones disponibles.
  5. Cliente compara precio, tiempo y taller.
  6. Cliente selecciona taller.
  7. Sistema registra selección y actualiza estado.
- **Postcondición:** cotización seleccionada y taller confirmado.
- **Excepciones:** sin cotizaciones, taller no disponible, taller fuera del tenant, error de confirmación.
- **Reglas recomendadas:** una cotización debe tener estado (`PENDIENTE`, `ACEPTADA`, `RECHAZADA`, `EXPIRADA`), monto, ETA y relación con incidente/taller/tenant.

### CU22. Integrar Pasarela de Pago

- **Propósito:** procesar el pago digital del servicio con pasarela, estado de transacción y comisión.
- **Actor principal:** Cliente.
- **Actores:** Cliente, Pasarela de Pago, Sistema.
- **Precondición:** cotización seleccionada o servicio finalizado con monto definido.
- **Flujo principal:**
  1. Cliente ingresa al módulo de pago.
  2. Sistema muestra monto total.
  3. Cliente selecciona método de pago.
  4. Plataforma envía solicitud a pasarela.
  5. Pasarela valida transacción.
  6. Plataforma recibe aprobación/rechazo.
  7. Pago se registra en base de datos.
  8. Cliente visualiza confirmación o rechazo.
- **Postcondición:** pago procesado y registrado.
- **Excepciones:** pago rechazado, error con pasarela, monto inválido, transacción duplicada, cancelación del proceso.
- **Nota:** en pruebas se menciona un flujo de comprobante manual y confirmación por taller/administrador; debe definirse si el flujo final es pasarela automática, QR manual o ambos.

### CU23. Visualizar Dashboard Operacional por Tenant

- **Propósito:** visualizar KPIs reales filtrados por tenant.
- **Actor principal:** Dueño del Taller.
- **Actores:** Administrador, Dueño del Taller.
- **Precondición:** usuario autenticado, tenant válido, permisos para indicadores.
- **Flujo principal:**
  1. Usuario accede al dashboard.
  2. Sistema identifica tenant.
  3. Backend consulta métricas.
  4. Sistema calcula KPIs.
  5. Dashboard presenta tarjetas, gráficos y tablas.
  6. Usuario aplica filtros.
- **Postcondición:** dashboard cargado con datos del tenant.
- **Excepciones:** datos insuficientes, usuario sin permisos, error de KPIs, intento de consultar otro tenant.
- **KPIs esperados:** tiempos promedio, incidentes por tipo, talleres eficientes, zonas críticas, cancelaciones, cumplimiento SLA.

### CU24. Gestionar Penalidad por Cancelación de Solicitud

- **Propósito:** aplicar una penalidad económica cuando el cliente cancela una solicitud en estado avanzado.
- **Actor principal:** Cliente.
- **Actores:** Cliente, Administrador.
- **Precondición:** emergencia registrada; estado cancelable como `ASIGNADA`, `EN_CAMINO` o `EN_ATENCION`.
- **Flujo principal:**
  1. Cliente ingresa al detalle de emergencia activa.
  2. Cliente selecciona cancelar solicitud.
  3. Sistema verifica estado actual y tiempo transcurrido.
  4. Sistema determina si corresponde penalidad.
  5. Si corresponde, calcula monto.
  6. Sistema actualiza estado como cancelado con/sin penalidad.
  7. Registra acción en bitácora y notifica al cliente.
- **Postcondición:** solicitud cancelada; penalidad registrada si corresponde.
- **Excepciones:** solicitud inexistente, incidente finalizado, usuario sin permisos, tenant incorrecto, error de cobro, fallo con pasarela.
- **Relaciones:** incluye CU17, CU11 y CU22.

### CU25. Generar Reportes Operacionales por Tenant

- **Propósito:** generar reportes filtrados por tenant, fecha, taller, tipo, estado o técnico.
- **Actor principal:** Dueño del Taller.
- **Actores:** Dueño del Taller, Administrador.
- **Precondición:** usuario autenticado, tenant válido, permisos, datos operacionales disponibles.
- **Flujo principal:**
  1. Usuario ingresa a reportes.
  2. Sistema identifica tenant.
  3. Usuario selecciona filtros.
  4. Sistema consulta datos del tenant.
  5. Sistema procesa métricas.
  6. Usuario selecciona formato de exportación.
  7. Sistema genera archivo descargable.
  8. Sistema registra acción para trazabilidad.
- **Postcondición:** reporte generado y disponible para descarga.
- **Excepciones:** sin permisos, tenant inválido, fechas incorrectas, sin datos, error de consulta, fallo de exportación.
- **Formatos mencionados en pruebas:** PDF, Excel o CSV.

### CU26. Generar Cobro de Multa por Cancelación de Servicio impulsado por IA

- **Estado documental:** aparece en la tabla de casos de uso y pruebas, pero no en el detalle formal de 3.1.3.
- **Propósito:** generar cobro de multa cuando el cliente cancela después de asignación, aceptación o proceso de atención.
- **Precondición:** cliente autenticado, emergencia asociada a tenant válido, estado cancelable con multa.
- **Flujo de prueba documentado:**
  1. Cliente solicita cancelar emergencia activa.
  2. Sistema valida estado del incidente.
  3. Sistema calcula multa según reglas.
  4. Sistema registra multa asociada a cliente/incidente.
  5. Sistema genera cobro pendiente.
  6. Sistema actualiza estado y notifica al cliente.
- **Recomendación:** decidir si CU26 es una extensión de CU24 o un caso independiente. Si se mantiene, definir claramente qué hace la IA: estimación de multa, evaluación de abuso, predicción de impacto operativo o clasificación de cancelación.

### CU27. Visualizar Mapa de Calor de Incidentes por Zona

- **Estado documental:** aparece en tabla y pruebas, pero no en el detalle formal de 3.1.3.
- **Propósito:** visualizar zonas con mayor concentración de incidentes en mapa interactivo.
- **Actores:** Dueño del Taller, Administrador.
- **Precondición:** usuario autenticado, tenant válido, permisos, incidentes con ubicación.
- **Flujo de prueba documentado:**
  1. Usuario ingresa a dashboard/análisis geográfico.
  2. Selecciona filtros: fechas, estado, tipo o tenant.
  3. Sistema valida tenant y permisos.
  4. Consulta incidentes geolocalizados.
  5. Genera mapa de calor.
  6. Identifica zona con mayor incidencia.
  7. Usuario analiza mapa para tomar decisiones operativas.
- **Recomendación:** vincularlo con CU23 Dashboard o tratarlo como submódulo analítico del paquete de KPIs.

---

## 12. Paquetes de análisis del segundo parcial

| Paquete | Responsabilidad | Casos de uso relacionados |
|---|---|---|
| Gestión Multi-Tenant | Administrar tenants, redes de talleres, asociación de usuarios/talleres/incidentes/métricas | CU16, CU17 |
| Seguridad y Aislamiento de Datos | Aplicar reglas de acceso y filtrado por tenant autenticado | CU17, CU16, CU23 |
| Modo Offline y Sincronización | Registrar emergencias sin conexión, almacenar localmente, sincronizar al recuperar conexión | CU18, CU19 |
| Tracking en Tiempo Real | Comunicación WebSocket, ubicación, estados, notificaciones inmediatas | CU20, CU11, CU10 |
| Analítica Operacional y KPIs | Calcular y visualizar indicadores reales por tenant | CU23, CU25, CU27 |
| Cotizaciones y Pagos Digitales | Cotizaciones, selección de taller, tiempo de reparación, pasarela de pago, penalidades | CU21, CU22, CU24, CU26 |

---

## 13. Relaciones relevantes entre casos de uso

- CU16 **incluye o requiere** CU17 para asegurar que los tenants no mezclen datos.
- CU18 **incluye o deriva en** CU19 cuando vuelve la conexión.
- CU20 se relaciona con CU11 y CU10 del primer parcial: actualizar estado y notificaciones.
- CU21 depende de CU17 porque las cotizaciones deben filtrarse por tenant.
- CU22 se relaciona con CU12 del primer parcial y CU17.
- CU23 se relaciona con CU14 del primer parcial y CU17.
- CU24 se relaciona con CU17, CU11 y CU22.
- CU25 se relaciona con CU17, CU14 y CU23.
- CU26 probablemente extiende CU24.
- CU27 probablemente extiende CU23.

---

## 14. Diseño y diagramas - descripción para IA

El documento contiene varios tipos de diagramas. Cuando la IA necesite reconstruirlos, debe considerar lo siguiente:

### 14.1 Diagramas de casos de uso

- Ciclo 4: CU16-CU20.
- Ciclo 5: CU21-CU25, con referencias visuales a CU17, CU14, CU23, CU11, CU22, CU10 y CU19.
- Página 32: estructura de modelos de casos de uso para ciclo 4 y ciclo 5.

### 14.2 Diagramas de comunicación

- Ciclo 4: CU16, CU17, CU18, CU19, CU20.
- Ciclo 5: CU21, CU22, CU23, CU24, CU25.
- Páginas 38-41: títulos y diagramas de comunicación por CU.

### 14.3 Análisis de clases

- Ciclo 4: CU16-CU20.
- Ciclo 5: CU21-CU25.
- Páginas 41-45: secciones de análisis de clase.

### 14.4 Diseño de arquitectura

- Arquitectura física: diagrama de despliegue.
- Arquitectura lógica: diagrama de paquetes.
- Páginas 47-48.

### 14.5 Diseño de datos

- Diagrama de clases.
- Mapeo.
- Normalización.
- Diagrama relacional.
- Tablas de volumen.
- Script SQL.
- Páginas 48-63.

### 14.6 Diagramas de secuencia

- Ciclo 4: CU16-CU20.
- Ciclo 5: CU21-CU25.
- Páginas 64-68.

### 14.7 Diagramas de navegación, red, estado y tiempo

- Navegación: páginas 69.
- Red: página 70.
- Estado: páginas 71-80.
- Tiempo: páginas 81-82.

---

## 15. Modelo de datos documentado

### 15.1 Tablas de volumen presentadas en el documento

El documento lista estas tablas en la sección de diseño lógico/relacional:

| # | Tabla | Propósito inferido |
|---:|---|---|
| 1 | `ROL` | Roles del sistema |
| 2 | `PERSONA` | Datos personales base |
| 3 | `USUARIO` | Credenciales, estado y rol |
| 4 | `BITACORA` | Auditoría de acciones |
| 5 | `VEHICULO` | Vehículos de usuarios/clientes |
| 6 | `EMPRESA` | Organización/empresa, probablemente tenant |
| 7 | `TALLER` | Talleres asociados a empresa/tenant |
| 8 | `SERVICIO_TALLER` | Servicios ofrecidos por taller |
| 9 | `EMERGENCIA` | Emergencias geolocalizadas |
| 10 | `NOTIFICACION` | Notificaciones por usuario/emergencia |
| 11 | `MENSAJE` | Mensajes de comunicación |
| 12 | `EVIDENCIA` | Archivos, transcripciones y diagnósticos |
| 13 | `EVALUACION` | Puntuación y comentario del servicio |
| 14 | `CONCEPTO_TARIFA` | Conceptos cobrables |
| 15 | `ORDEN_COBRO` | Orden económica por emergencia/empresa |
| 16 | `DETALLE_COBRO` | Detalle de conceptos cobrados |
| 17 | `PAGO` | Pagos realizados |

### 15.2 Script SQL incluido

El script SQL del documento crea un esquema diferente, basado en UUID y tablas:

- `USUARIOS`
- `CLIENTES`
- `TALLERES`
- `TECNICOS`
- `VEHICULOS`
- `INCIDENTES`
- `EVIDENCIAS`
- `HISTORIAL_INCIDENTES`
- `ASIGNACIONES`
- `PAGOS`

También crea enums:

- `rol_enum`
- `estado_incidente_enum`
- `prioridad_enum`
- `clasificacion_enum`
- `tipo_evidencia_enum`
- `estado_pago_enum`

Índices relevantes:

- Pagos por estado, taller y cliente.
- Incidentes por estado y cliente.
- Asignaciones por taller y técnico.
- Índices geográficos GIST en ubicación de incidentes y técnicos.

### 15.3 Observación crítica del modelo de datos

Existe una inconsistencia entre las **tablas de volumen** y el **script SQL**:

- Las tablas de volumen usan nombres como `ROL`, `PERSONA`, `USUARIO`, `EMPRESA`, `EMERGENCIA`, `ORDEN_COBRO`.
- El script SQL usa `USUARIOS`, `CLIENTES`, `TALLERES`, `TECNICOS`, `INCIDENTES`, `PAGOS`.
- El segundo parcial habla de multi-tenant, cotizaciones, reportes, penalidades y mapa de calor, pero el script no define explícitamente tablas como `TENANTS`, `COTIZACIONES`, `PENALIDADES`, `REPORTES`, `EVENTOS_WEBSOCKET`, `EMERGENCIAS_OFFLINE` o `SYNC_LOG`.

Para una implementación real, conviene consolidar un único modelo de datos y agregar campos/tablas específicas para el segundo parcial.

---

## 16. Entidades sugeridas para completar los ciclos 4 y 5

Estas entidades no necesariamente están completas en el PDF, pero son necesarias para implementar correctamente lo que el documento exige:

| Entidad sugerida | Propósito |
|---|---|
| `tenants` | Registrar organizaciones o redes de talleres |
| `tenant_users` | Asociar usuarios a tenants y roles internos |
| `tenant_talleres` | Asociar talleres a tenants |
| `cotizaciones` | Registrar cotizaciones de talleres para incidentes |
| `pagos_pasarela` | Registrar solicitudes/respuestas de pasarela |
| `penalidades` | Registrar multas por cancelación |
| `sync_queue` | Controlar emergencias offline pendientes |
| `tracking_events` | Guardar eventos WebSocket/GPS relevantes |
| `kpi_snapshots` | Guardar métricas calculadas por tenant/periodo |
| `reportes_generados` | Auditar generación de reportes |
| `heatmap_points` o vista SQL | Consolidar incidentes por zona para mapa de calor |

Campos críticos recomendados:

- `tenant_id` en casi todas las tablas operativas.
- `created_at`, `updated_at`, `deleted_at`.
- `created_by`, `updated_by`.
- `sync_status` para flujo offline.
- `external_payment_id` para pasarela.
- `local_incident_id` para idempotencia offline.
- `status_reason` para cancelaciones y rechazos.

---

## 17. Arquitectura técnica de implementación

### 17.1 Backend - Python + FastAPI

Se eligió Python con FastAPI por:

- Rendimiento alto.
- Soporte asíncrono.
- Integración natural con IA.
- Validación de datos.
- Soporte de WebSockets.
- Capacidad para manejar emergencias, notificaciones, tracking y asignación sin bloquear el servidor.

El documento indica uso de consultas SQL puras con `psycopg2`, centralizadas en repositorios, para tener control transaccional y aplicar filtros por tenant.

### 17.2 Aplicación móvil - Flutter / Dart

Flutter permite:

- Compilar para Android e iOS desde un código base.
- Capturar GPS y multimedia.
- Implementar modo offline.
- Encolar emergencias sin internet.
- Sincronizar en segundo plano.

### 17.3 Aplicación web - Angular

Angular se usa para:

- Portal de talleres.
- Panel administrativo.
- Dashboards complejos.
- Visualización de KPIs.
- Uso de RxJS para estados reactivos en tiempo real.
- PWA para sesiones inestables.

### 17.4 Base de datos - PostgreSQL + PostGIS

PostgreSQL se selecciona por:

- Confiabilidad transaccional.
- Escalabilidad.
- Seguridad.
- Soporte JSON/JSONB.
- Integración con PostGIS para geolocalización.
- Índices GIST para ubicación de incidentes y técnicos.

### 17.5 Control de versiones y servicios externos

- GitHub para código fuente, ramas, issues y trazabilidad.
- Servicios Cloud/IA para audio a texto y visión artificial.

---

## 18. Estrategia de pruebas

El documento conserva cuatro tipos de pruebas:

| Tipo de prueba | Objetivo | Enfoque |
|---|---|---|
| Unidad | Verificar componentes individuales | Caja blanca, backend y base de datos |
| Integración | Validar comunicación entre paquetes | Flujo completo por CU |
| Validación | Confirmar requisitos desde perspectiva del usuario | Caja negra |
| Aceptación | Aprobar funcionalidad en ambiente de prueba | Simulación de uso real |

Objetivos de prueba:

- Validar funcionalidad.
- Verificar integridad del sistema.
- Asegurar usabilidad.
- Validar procesamiento inteligente.
- Detectar defectos temprano.

---

## 19. Casos de prueba - Ciclo 4

| CU | Caso de prueba | Precondición | Resultado esperado |
|---|---|---|---|
| CU16 | Administrar tenants y redes | Admin autenticado con permisos | Tenant registrado, usuarios/talleres asociados, operación exitosa |
| CU17 | Validar aislamiento de datos | Usuario autenticado con tenant válido | Solo visualiza datos del tenant; acceso externo bloqueado |
| CU18 | Registrar emergencia offline | Cliente autenticado sin conexión | Emergencia guardada localmente y marcada pendiente |
| CU19 | Sincronizar pendientes | Emergencia local pendiente + conexión restaurada | Incidente registrado en backend y estado local sincronizado |
| CU20 | Tracking en vivo WebSocket | Emergencia asignada y técnico asignado | Ubicación/estado se actualizan en tiempo real |

---

## 20. Casos de prueba - Ciclo 5

| CU | Caso de prueba | Precondición | Resultado esperado |
|---|---|---|---|
| CU21 | Cotizaciones y selección de taller | Incidente registrado y disponible para cotización | Cotización registrada, filtrada por tenant y taller seleccionado |
| CU22 | Pasarela de pagos | Cotización o servicio con monto definido | Pago registrado, confirmado o pendiente según flujo |
| CU23 | Dashboard operacional por tenant | Usuario con tenant y permisos | KPIs y gráficos calculados desde datos reales del tenant |
| CU24 | Penalidad por cancelación | Emergencia activa en estado cancelable | Incidente cancelado con/sin penalidad y registro histórico |
| CU25 | Reportes operacionales | Usuario con permisos y datos disponibles | Reporte generado en PDF/Excel/CSV y disponible para descarga |
| CU26 | Cobro de multa por cancelación | Incidente avanzado cancelado | Multa registrada y cobro pendiente generado |
| CU27 | Mapa de calor por zona | Incidentes con ubicación y permisos | Mapa de calor muestra zonas críticas del tenant |

---

## 21. Reglas de negocio consolidadas

1. Un usuario debe pertenecer a un tenant para consultar datos operativos.
2. Todo dato operativo debe filtrarse por tenant.
3. Una emergencia offline debe tener identificador local para evitar duplicados.
4. Una emergencia offline debe cambiar de estado cuando se sincroniza.
5. El tracking solo puede iniciarse si existe técnico asignado.
6. El WebSocket debe validar token, rol, tenant e incidente.
7. Una cotización debe pertenecer al mismo tenant del incidente.
8. El cliente solo puede seleccionar cotizaciones disponibles y válidas.
9. El pago debe asociarse a incidente, cliente, taller/asignación y estado.
10. La penalidad solo aplica si la cancelación ocurre en estado avanzado o según tiempo transcurrido.
11. Reportes y dashboards solo deben consultar datos del tenant autenticado.
12. Todo cambio sensible debe registrarse en bitácora/historial.

---

## 22. Observaciones técnicas e inconsistencias detectadas

Estas observaciones son útiles para que una IA no replique errores del documento:

1. **CU26 y CU27 aparecen incompletos.** Se listan y tienen casos de prueba, pero no se desarrollan igual que CU16-CU25 en la sección de detalle de casos de uso.
2. **El modelo de datos no refleja completamente multi-tenant.** El script SQL no incluye una tabla `TENANTS` ni `tenant_id` explícito en `INCIDENTES`, `PAGOS`, `TALLERES`, etc.
3. **Inconsistencia entre tablas de volumen y script SQL.** Las tablas conceptuales usan estructura `SERIAL`, `EMPRESA`, `EMERGENCIA`; el script usa UUID y nombres distintos.
4. **CU20 tiene excepción incorrecta.** Dice “credenciales incorrectas o usuario no registrado”, más propio de login que de tracking WebSocket.
5. **La sección 3.4.1.3 Sistemas Operativos repite contenido de Base de Datos.** Debe reemplazarse por compatibilidad real: Windows, Linux, macOS, Android, iOS, navegador web/PWA.
6. **CU23 cambia de nombre en pruebas.** En requisitos se llama “Visualizar dashboard operacional por tenant”; en pruebas aparece “Generar con IA dashboard operacional por tenant”. Debe normalizarse.
7. **CU22 alterna entre pasarela automática y comprobante manual.** Se debe decidir si el flujo será pago digital automático, QR manual, o ambos.
8. **No se definen tablas para cotizaciones.** CU21 requiere una entidad formal `cotizaciones`.
9. **No se definen tablas para penalidades.** CU24/CU26 requieren entidad `penalidades` o integración con `orden_cobro/detalle_cobro`.
10. **No se define almacenamiento local.** CU18/CU19 requieren un diseño explícito de cache/local DB.
11. **No se define protocolo WebSocket.** CU20 requiere eventos, rooms/canales, autenticación y payloads.
12. **No se especifica estrategia de autorización.** Para multi-tenant se recomienda RBAC + filtrado por tenant + auditoría.
13. **El script usa `gen_random_uuid()` pero solo crea `postgis`.** En PostgreSQL puede requerirse `CREATE EXTENSION IF NOT EXISTS pgcrypto;`, aunque en Supabase puede estar disponible.

---

## 23. Recomendaciones para mejorar la documentación final

- Crear un **SDD del segundo parcial** con arquitectura multi-tenant, offline, realtime y analítica.
- Normalizar la lista oficial de casos de uso: decidir si el ciclo 5 termina en CU25 o incluye CU26-CU27.
- Agregar detalle formal para CU26 y CU27 si se mantienen.
- Consolidar un único modelo de datos.
- Agregar `tenant_id` a entidades operativas.
- Agregar tablas de `cotizaciones`, `penalidades`, `sync_queue`, `tracking_events` y `reportes_generados`.
- Diseñar eventos WebSocket: `tracking:update`, `incident:status_changed`, `notification:new`, `technician:location`.
- Definir estrategia de idempotencia para sincronización offline.
- Definir estrategia de seguridad para WebSockets y reportes.
- Separar pagos normales de penalidades.
- Añadir pruebas negativas: acceso a otro tenant, pérdida de conexión, duplicado offline, token expirado, pasarela rechazada.

---

## 24. Prompt recomendado para usar este documento con IA

```text
Actúa como arquitecto de software senior y AI Engineer.

Voy a trabajar sobre la Plataforma Inteligente de Atención de Emergencias Vehiculares.
Toma este Markdown como fuente de verdad del segundo parcial, correspondiente a los ciclos 4 y 5.

Debes respetar:
- Arquitectura SaaS multi-tenant.
- Aislamiento de datos por tenant.
- Backend FastAPI.
- Base de datos PostgreSQL + PostGIS.
- App móvil Flutter.
- App web Angular.
- Comunicación en tiempo real mediante WebSockets.
- Modo offline con sincronización automática.
- Dashboards, KPIs y reportes por tenant.
- Cotizaciones, pagos y penalidades.

Antes de proponer código:
1. Identifica el caso de uso involucrado.
2. Indica qué paquete funcional se ve afectado.
3. Revisa si existe impacto en tenant_id, seguridad o trazabilidad.
4. Propón cambios por archivo o módulo.
5. No inventes dependencias externas sin justificar.
6. No mezcles datos entre tenants.
7. Señala inconsistencias si detectas que el documento no define algo suficiente.
```

---

## 25. Mapa rápido para IA

```text
Proyecto: Plataforma Inteligente de Atención de Emergencias Vehiculares
Fase: Segundo Parcial
Ciclos: 4 y 5

Ciclo 4:
- CU16: Administrar tenants y redes de talleres
- CU17: Validar aislamiento de datos por tenant
- CU18: Registrar emergencia offline
- CU19: Sincronizar emergencias pendientes
- CU20: Tracking en vivo con WebSockets

Ciclo 5:
- CU21: Cotizaciones y selección de taller
- CU22: Pasarela de pagos
- CU23: Dashboard operacional por tenant
- CU24: Penalidad por cancelación
- CU25: Reportes operacionales por tenant
- CU26: Cobro de multa por cancelación impulsado por IA
- CU27: Mapa de calor de incidentes por zona

Paquetes:
- Gestión Multi-Tenant
- Seguridad y Aislamiento de Datos
- Modo Offline y Sincronización
- Tracking en Tiempo Real
- Analítica Operacional y KPIs
- Cotizaciones y Pagos Digitales

Stack:
- Backend: FastAPI + Python
- DB: PostgreSQL + PostGIS
- Web: Angular
- Mobile: Flutter
- Realtime: WebSockets
- Offline: PWA / local storage / sincronización
```

---

# 26. Transcripción textual por páginas para trazabilidad

> Esta sección conserva el contenido textual extraído del PDF por páginas. Algunos diagramas contienen información visual no completamente representada en texto; para ellos se incluyeron descripciones estructuradas en las secciones anteriores.


### Página 1

```text
UNIVERSIDAD AUTÓNOMA GABRIEL RENÉ MORENO
FACULTAD DE INGENIERÍA EN CIENCIAS DE LA COMPUTACIÓN Y
TELECOMUNICACIONES


Plataforma Inteligente de Atención de Emergencias Vehiculares


Materia: Sistemas de Información II
Sigla: INF412
Docente: Msc. Ing. Angélica Garzón Cuellar
Grupo: 22
Integrantes:
-
Melgar Gushi Diego
-
Ortiz Montero Luis Enrique


Semestre I/2026
```


### Página 2

```text
Contenido
1.
PERFIL .......................................................................................................................................................... 5
1.1.
Introducción .......................................................................................................................................... 5
1.2 Objetivo General ......................................................................................................................................... 5
1.3 Objetivos Específicos .................................................................................................................................. 5
1.4 Descripción del Problema ........................................................................................................................... 5
1.5 Alcance ......................................................................................................................................................... 6
2.
Marco Teórico ............................................................................................................................................... 7
3.
Flujo de Trabajo ......................................................................................................................................... 13
3.1 Captura de requisitos ............................................................................................................................... 13
3.1.1 Encontrar Actores y Casos de uso ........................................................................................................ 13
3.1.2 Priorizar Casos de Uso ......................................................................................................................... 17
3.1.3 Detallar Casos de Uso .......................................................................................................................... 18
CICLO #4...................................................................................................................................................... 18
CICLO #5...................................................................................................................................................... 23
3.1.4 Prototipar la Interfaz de Usuario ..................................................................................................... 27
CICLO #5...................................................................................................................................................... 30
3.1.5 Estructurar Modelos de Casos de Uso ............................................................................................. 32
CICLO #4...................................................................................................................................................... 32
CICLO #5...................................................................................................................................................... 32
3.2 Análisis ....................................................................................................................................................... 33
3.2.1 Análisis de Arquitectura ....................................................................................................................... 33
3.2.1.1 Identificar Paquetes ....................................................................................................................... 33
3.2.1.2 Relacionar Paquetes y Casos de Uso ................................................................................................ 34
3.2.1.3 Vista de Paquetes .............................................................................................................................. 35
Paquete de Gestión Multi-Tenant ............................................................................................................. 35
Paquete de Seguridad y Aislamiento de Datos ......................................................................................... 36
Paquete de Modo offline y Sincronización ............................................................................................... 36
Paquete de Tracking en Tiempo Real ....................................................................................................... 36
Paquete de Analítica Operacional y KPIs ................................................................................................. 37
Paquete de Cotizaciones y Pagos .............................................................................................................. 37
3.2.2 Diagramas de Comunicación ............................................................................................................... 38
CICLO #4.................................................................................................................................................. 38
CICLO #5.................................................................................................................................................. 39
3.2.3 Analizar una clase ................................................................................................................................ 41
3.2.4 Analizar un Paquete ............................................................................................................................. 46
```


### Página 3

```text
3.3 Diseño ......................................................................................................................................................... 47
3.3.1 Diseño de Arquitectura ........................................................................................................................ 47
Arquitectura Física (Diagrama de Despliegue) ......................................................................................... 47
Arquitectura Lógica (Diagrama de Paquetes) ........................................................................................... 48
3.3.2 Diseño de Datos .................................................................................................................................. 48
3.3.2.1 Diseño de Datos Lógicos .............................................................................................................. 48
3.3.3 Diseño de Caso de Uso ........................................................................................................................ 64
Diagrama de Secuencia ................................................................................................................................. 64
CICLO #4.................................................................................................................................................. 64
3.3.4 Diagrama de Navegación ..................................................................................................................... 69
CICLO #4.................................................................................................................................................. 69
CICLO #5.................................................................................................................................................. 69
3.3.5 Diagrama de Red .................................................................................................................................. 70
3.3.6 Diagrama de Estado ............................................................................................................................. 71
CICLO #4.................................................................................................................................................. 71
CICLO #5.................................................................................................................................................. 76
3.3.7 Diagrama de Tiempo ............................................................................................................................ 81
CICLO #4.................................................................................................................................................. 81
CICLO #5.................................................................................................................................................. 82
3.4 Implementación ......................................................................................................................................... 83
3.4.1 Elección de Plataforma de Desarrollo de Software .............................................................................. 83
3.4.1.1 Lenguaje de Programación ............................................................................................................ 83
3.4.1.2 Base de Datos ................................................................................................................................ 83
3.4.1.3 Sistemas Operativos ...................................................................................................................... 84
3.4.1.4 Otros .............................................................................................................................................. 85
3.4.2 Arquitectura del Sistema ...................................................................................................................... 85
3.4.3 Arquitectura del Subsistema ................................................................................................................ 86
3.5 Flujo de Trabajo: Pruebas ....................................................................................................................... 88
3.5.1 Planificar Pruebas ................................................................................................................................ 88
3.5.2 Objetivos de la Prueba ......................................................................................................................... 88
3.5.3 Estrategia de Pruebas ........................................................................................................................... 89
3.5.4 Casos de Pruebas (Implementar Pruebas) ............................................................................................ 90
CICLO #4.................................................................................................................................................. 90
CICLO #5.................................................................................................................................................. 95
Conclusión ......................................................................................................................................................... 106
Recomendación ................................................................................................................................................. 107
Bibliografía ........................................................................................................................................................ 108
```


### Página 4

```text
URL y QR .......................................................................................................................................................... 108
```


### Página 5

```text
1. PERFIL
1.1.
Introducción
En la actualidad, la transformación digital ha permitido que múltiples sectores incorporen soluciones
tecnológicas capaces de optimizar procesos, reducir tiempos de respuesta y mejorar la experiencia de los
usuarios. Dentro de este contexto, los sistemas de atención de emergencias vehiculares representan una
herramienta fundamental para brindar asistencia rápida, eficiente y trazable ante incidentes ocurridos en
carretera o zonas urbanas.
En la primera etapa del proyecto se desarrolló una plataforma inteligente de atención de emergencias
vehiculares compuesta por una aplicación web, una aplicación móvil, un backend basado en FastAPI y una
base de datos en PostgreSQL. El sistema permitía registrar incidentes, asignar talleres mecánicos, gestionar
usuarios, utilizar geolocalización y realizar seguimiento básico del estado de las emergencias.
En esta segunda fase, el proyecto evoluciona hacia una solución más robusta y cercana a un entorno real de
producción, incorporando funcionalidades avanzadas como comunicación en tiempo real mediante
websockets, funcionamiento offline con sincronización automática, dashboards con KPIs operacionales y
arquitectura SaaS multi-tenant para soportar múltiples organizaciones dentro de una misma plataforma.
De esta manera, se busca mejorar la escalabilidad, trazabilidad y eficiencia operacional del sistema,
aplicando además la metodología PUDS-UML 2.5+ durante todo el proceso de desarrollo.
1.2 Objetivo General
Evolucionar la plataforma inteligente de atención de emergencias vehiculares mediante la implementación
de funcionalidades de tiempo real, sincronización offline, analítica operacional y arquitectura SaaS multi-
tenant, con el fin de mejorar la eficiencia, trazabilidad escalabilidad y gestión de los servicios dentro de un
entorno más cercano a una operación real.
1.3 Objetivos Específicos

•
Implementar un módulo de comunicación en tiempo real mediante websockets, para el seguimiento
y actualización de incidentes vehiculares.
•
Desarrollar un sistema de funcionamiento offline que permita registrar emergencias sin conexión a
internet y sincronizarlas automáticamente cuando la conexión sea restablecida.
•
Incorporar dashboards operacionales con KPIs obtenidos desde datos reales almacenados en la base
de datos.
•
Implementar una arquitectura SaaS multi-tenant que permita administrar múltiples organizaciones o
redes de talleres de manera independiente.
•
Mejorar la trazabilidad y monitoreo de los servicios de asistencia vehicular durante todo el flujo de
atención.
•
Aplicar metodología PUDS junto a UML 2.5+ en las etapas de análisis, diseño, implementación y
pruebas del sistema.

1.4 Descripción del Problema
En la primera fase del proyecto se desarrolló una plataforma básica para la atención de emergencias
vehiculares, permitiendo registrar incidentes, asignar talleres y realizar seguimiento de los servicios. Sin
embargo, el sistema aún presenta limitaciones importantes para operar en un entorno real y escalable. Uno de
los principales problemas identificados es la falta de actualización en tiempo real, ya que los usuarios no
pueden visualizar inmediatamente los cambios de estado de una emergencia o el seguimiento del taller
asignado. Asimismo, la aplicación depende completamente de una conexión estable a internet, lo que
dificulta el registro de incidentes en zonas con baja cobertura o sin acceso a red. Además, el sistema no
cuenta con herramienta de analítica operacional que permitan monitorear indicadores de desempeño, tiempos
```


### Página 6

```text
de respuesta o niveles de cumplimiento de servicio. Esto limita la capacidad de supervisión y toma de
decisiones por parte de los administradores.
Por otra parte, la plataforma actual fue diseñada para una sola organización, por lo que no existe un
mecanismo que permita separar y administrar la información de múltiples empresas o redes de talleres dentro
de un mismo sistema. Debido a estas limitaciones, surge la necesidad de evolucionar la plataforma hacia una
solución más robusta, escalable y orientada a operación real, incorporando funcionalidades de tiempo real,
sincronización offline, dashboards operacionales y arquitectura SaaS multi-tenant.
1.5 Alcance
El presente proyecto contempla la evolución de la plataforma inteligente de atención de emergencias
vehiculares desarrollada en la primera fase, incorporando nuevas funcionalidades orientadas a mejorar la
operación, escalabilidad y experiencia de los usuarios. El sistema incluirá una aplicación web, una aplicación
móvil, un backend desarrollado con FastAPI y una base de datos PostgreSQL, integrando mecanismos de
comunicación en tiempo real mediante websockets, funcionamiento offline con sincronización automática,
dashboards operacionales con KPIs y arquitectura SaaS multi-tenant. La plataforma permitirá registrar
emergencias vehiculares, asignar talleres, realizar seguimiento del estado de los incidentes, gestionar
cotizaciones, seleccionar talleres, visualizar tiempos estimados de reparación y efectuar pagos mediante
integración con pasarelas de pago. Asimismo, el sistema garantizará el aislamiento lógico de la información
entre diferentes organizaciones o redes de talleres, permitiendo que múltiples tenants utilicen la misma
plataforma de manera independiente y segura.
El alcance del proyecto se limita al desarrollo funcional y académico de la solución, por lo que no contempla
despliegues productivos a gran escala ni integraciones bancarias reales en ambientes comerciales.
```


### Página 7

```text
2. Marco Teórico
Módulo I: Comunicación En Tiempo Real
Comunicación en Tiempo Real
La comunicación en tiempo real corresponde a un modelo de intercambio de información donde los datos son
transmitidos y actualizados instantáneamente entre sistemas conectados. Este tipo de comunicación es
ampliamente utilizado en aplicaciones distribuidas que requieren sincronización inmediata de eventos y
reducción de latencia en la transmisión de información.
Los sistemas en tiempo real permiten mantener consistencia operativa entre múltiples usuarios y dispositivos
conectados simultáneamente, optimizando la velocidad de respuesta y mejorando la experiencia de interacción.
La comunicación en tiempo real constituye un componente fundamental en aplicaciones modernas orientadas a
monitoreo, seguimiento de procesos y administración de eventos dinámicos.
WebSockets
WebSocket es un protocolo de comunicación bidireccional diseñado para establecer conexiones persistentes
entre cliente y servidor sobre una única sesión TCP.
A diferencia del protocolo HTTP tradicional basado en solicitudes independientes, WebSockets permite
mantener una conexión abierta y continua, facilitando el intercambio simultáneo de información entre ambas
partes.
Las principales características de WebSockets son:
•
Comunicación bidireccional.
•
Baja latencia.
•
Conexión persistente.
•
Transmisión continua de datos.
•
Reducción de sobrecarga de red.
Este protocolo es ampliamente utilizado en sistemas de mensajería instantánea, monitoreo en vivo, videojuegos
en línea, plataformas financieras y aplicaciones de seguimiento en tiempo real.
Tracking en Tiempo Real
El tracking en tiempo real corresponde al proceso de monitoreo continuo de ubicación, estado o movimiento de
recursos dentro de un sistema digital.
El seguimiento en tiempo real utiliza tecnologías de geolocalización y transmisión instantánea de datos para
representar dinámicamente la posición y comportamiento de entidades móviles.
Las soluciones de tracking permiten:
•
Supervisión continua.
•
Control operacional.
•
Optimización de rutas.
•
Monitoreo de desplazamientos.
•
Gestión de recursos móviles.
```


### Página 8

```text
Geolocalización
La geolocalización es una tecnología utilizada para determinar la ubicación geográfica de un dispositivo, usuario
o recurso mediante coordenadas espaciales obtenidas por sistemas de posicionamiento global.
La geolocalización puede implementarse utilizando:
•
GPS.
•
Redes móviles.
•
Wi-Fi.
•
Servicios de mapas digitales.
Esta tecnología es ampliamente utilizada en aplicaciones de navegación, transporte, logística, rastreo y servicios
de asistencia.
Módulo II: Funcionamiento Offline Y Sincronización
Funcionamiento Offline
El funcionamiento offline corresponde a la capacidad de una aplicación para continuar operando parcialmente
sin conexión a internet.
Las aplicaciones offline permiten almacenar información localmente y ejecutar determinadas funcionalidades
incluso en ausencia de conectividad de red.
Este enfoque incrementa disponibilidad, continuidad operativa y resiliencia del sistema frente a fallos de
conexión.
Las aplicaciones con soporte offline deben garantizar:
•
Persistencia temporal de datos.
•
Integridad de información.
•
Continuidad funcional.
•
Recuperación posterior de sincronización.
Sincronización de Datos
La sincronización de datos es el proceso mediante el cual la información almacenada localmente es actualizada
e integrada posteriormente con un servidor central para mantener consistencia entre dispositivos y sistemas
distribuidos.
La sincronización permite:
•
Actualización de registros.
•
Resolución de conflictos.
•
Prevención de duplicados.
•
Consistencia de información.
•
Recuperación de datos pendientes.
Este mecanismo es fundamental en aplicaciones móviles modernas y sistemas distribuidos.
```


### Página 9

```text
Persistencia Local
La persistencia local consiste en almacenar información directamente en el dispositivo cliente mediante bases de
datos locales, almacenamiento interno o mecanismos de caché.
La persistencia local permite conservar información temporal incluso cuando la aplicación pierde conectividad
con el servidor principal.
Entre las tecnologías utilizadas para persistencia local destacan:
•
SQLite.
•
IndexedDB.
•
Local Storage.
•
Caché de aplicaciones.
Aplicaciones Web Progresivas (PWA)
Progressive Web Apps constituyen aplicaciones web modernas que integran características propias de
aplicaciones móviles nativas utilizando tecnologías web estándar.
Las Progressive Web Apps permiten:
•
Funcionamiento offline.
•
Instalación en dispositivos.
•
Notificaciones push.
•
Almacenamiento local.
•
Optimización de rendimiento.
Las PWAs mejoran accesibilidad, disponibilidad y experiencia de usuario sin depender de tiendas de
aplicaciones tradicionales.
Service Workers
Los Service Workers son scripts ejecutados en segundo plano dentro del navegador que permiten interceptar
solicitudes de red y administrar recursos almacenados localmente.
Los Service Workers facilitan:
•
Funcionamiento offline.
•
Gestión de caché.
•
Sincronización en segundo plano.
•
Optimización de carga de recursos.
Estos componentes representan uno de los elementos fundamentales de las aplicaciones web progresivas.
```


### Página 10

```text
Módulo III: Analítica Operacional Y KPIs
Analítica Operacional
La analítica operacional corresponde al uso de datos generados por un sistema para monitorear desempeño,
detectar patrones y apoyar procesos de toma de decisiones.
La analítica operacional transforma información almacenada en conocimiento útil mediante técnicas de
procesamiento, visualización e interpretación de datos.
Este enfoque permite:
•
Supervisión de operaciones.
•
Evaluación de desempeño.
•
Identificación de tendencias.
•
Optimización de procesos.
•
Apoyo estratégico.
Dashboard
Un dashboard es una interfaz visual diseñada para representar información relevante mediante gráficos, tablas e
indicadores estadísticos.
Los dashboards permiten consolidar grandes volúmenes de datos en paneles interactivos que facilitan monitoreo
y análisis operacional.
Sus principales objetivos son:
•
Visualización rápida de información.
•
Supervisión en tiempo real.
•
Evaluación de indicadores.
•
Apoyo a la toma de decisiones.
KPIs (Key Performance Indicators)
Los KPIs son indicadores clave de rendimiento utilizados para medir eficiencia, desempeño y cumplimiento de
objetivos organizacionales.
Los indicadores permiten evaluar resultados cuantificables asociados a procesos específicos.
Entre los principales tipos de KPIs destacan:
•
Indicadores de tiempo.
•
Indicadores de productividad.
•
Indicadores de calidad.
•
Indicadores de cumplimiento.
•
Indicadores de eficiencia operacional.
Los KPIs constituyen herramientas esenciales para el monitoreo y control de procesos empresariales.
SLA (Service Level Agreement)
El SLA o Acuerdo de Nivel de Servicio corresponde a un conjunto de parámetros que definen niveles mínimos
esperados de calidad y tiempos de respuesta dentro de un servicio.
```


### Página 11

```text
Los SLA permiten establecer métricas objetivas para evaluar desempeño operacional y cumplimiento de
compromisos.
Su utilización es frecuente en:
•
Servicios tecnológicos.
•
Plataformas SaaS.
•
Sistemas de soporte.
•
Infraestructuras críticas.
Trazabilidad
La trazabilidad corresponde a la capacidad de registrar y monitorear el historial completo de eventos y
operaciones generadas dentro de un sistema.
La trazabilidad permite:
•
Auditoría de procesos.
•
Seguimiento histórico.
•
Control de actividades.
•
Verificación de operaciones.
•
Supervisión operacional.
Este principio resulta fundamental en plataformas críticas donde se requiere control y transparencia de
información.
Módulo IV: Arquitectura SaaS Multi-Tenant
Arquitectura SaaS
Software as a Service corresponde a un modelo de distribución de software donde las aplicaciones son ofrecidas
como servicios accesibles mediante internet.
En arquitecturas SaaS:
•
La infraestructura es centralizada.
•
Los usuarios acceden remotamente.
•
El mantenimiento es administrado por el proveedor.
•
Las actualizaciones son unificadas.
El modelo SaaS favorece escalabilidad, optimización de recursos y reducción de costos operativos.
Arquitectura Multi-Tenant
La arquitectura multi-tenant constituye un modelo de diseño donde múltiples organizaciones utilizan una misma
plataforma compartiendo infraestructura, pero manteniendo separación lógica de información.
Cada organización participante es denominada tenant y opera de forma independiente dentro del sistema
compartido.
La arquitectura multi-tenant permite:
•
Compartición eficiente de recursos.
•
Escalabilidad horizontal.
```


### Página 12

```text
•
Administración centralizada.
•
Optimización de infraestructura.

Tenant
El tenant representa una entidad organizacional independiente dentro de una plataforma multi-tenant.
Cada tenant posee:
•
Usuarios propios.
•
Información independiente.
•
Configuraciones particulares.
•
Recursos asociados.
El concepto de tenant constituye la base lógica para la separación de datos dentro de plataformas SaaS
modernas.
Aislamiento de Datos
El aislamiento de datos es un principio de seguridad utilizado en arquitecturas multi-tenant para impedir que una
organización acceda a información perteneciente a otra.
El aislamiento puede implementarse mediante:
•
Filtrado lógico.
•
Restricciones de acceso.
•
Esquemas separados.
•
Bases de datos independientes.
Este mecanismo garantiza privacidad, confidencialidad e integridad de información.
Escalabilidad
La escalabilidad corresponde a la capacidad de un sistema para soportar crecimiento de usuarios, datos y
operaciones sin afectar significativamente el rendimiento.
Los sistemas escalables permiten:
•
Incrementar capacidad operativa.
•
Optimizar recursos.
•
Adaptarse al crecimiento.
```


### Página 13

```text
3. Flujo de Trabajo
3.1 Captura de requisitos
3.1.1 Encontrar Actores y Casos de uso

Actor
Rol
Función en el sistema
Cliente (Conductor)
Usuario final que solicita el
auxilio mecánico.
Registrarse en la app y
registrar sus vehículos.
Reportar emergencias
enviando ubicación, fotos y
audio. Visualizar el estado de
su solicitud, el taller
asignado y realizar pagos
Dueño del Taller
Responsable de la gestión
operativa del taller en la
plataforma web.
Registrar el taller y gestionar
a sus técnicos. Visualizar
solicitudes disponibles con
información enriquecida por
IA. Aceptar o rechazar
solicitudes y asignar órdenes
según ubicación y
disponibilidad.
Técnico Mecánico
Operador encargado de
brindar la asistencia física al
cliente.
Recibir la orden de trabajo
asignada por el taller.
Actualizar el estado del
servicio en tiempo real (en
proceso, atendido).
Proporcionar su ubicación
para la estimación del tiempo
de llegada.
Módulos de IA
Encargado de procesar datos
multimodales.
Realizar la transcripción
automática de audio a texto.
Generar resúmenes
automáticos. Determinar el
nivel de prioridad de la
emergencia.
Administrador del Sistema
Responsable de la gestión
global y mantenimiento de la
plataforma.
Gestionar la autenticación,
autorización y perfiles de
usuarios y talleres.
Supervisar la integridad de
los datos en la base de datos.
Monitorear el motor de
asignación y el sistema de
notificaciones.

Casos de uso:
•
CU16: Administrar tenants y redes de talleres.
•
CU17: Validar aislamiento de datos por tenant.
•
CU18: Registrar emergencia en modo offline.
•
CU19: Sincronizar emergencias pendientes.
•
CU20: Gestionar emergencias pendientes.
•
CU21: Gestionar cotizaciones y selección de taller.
•
CU22: Procesar pago mediante pasarela de pagos.
```


### Página 14

```text
•
CU23: Visualizar dashboard operacional por tenant.
•
CU24: Gestionar penalidad por cancelación de solicitud
•
CU25: Generar reportes operacionales por tenant

Tabla de Casos de Uso Primer Parcial:
ID
Nombre del Caso de Uso
Justificación
CU1
Gestionar Inicio/Cierre de sesión
Falta de control de acceso seguro
y autenticado para los diferentes
perfiles del sistema.
CU2
Gestionar Roles y Permisos
Inexistencia de un mecanismo
para controlar las funcionalidades
específicas de cada usuario,
asegurando que solo los talleres
vean sus solicitudes.
CU3
Registrar Cliente y Vehículo
Proceso desorganizado para el
registro de datos del conductor y
las especificaciones técnicas de
los vehículos atendidos.
CU4
Registrar Taller y Técnicos
Ausencia de un registro
estructurado de proveedores de
servicio y su personal disponible
para la atención de emergencias.
CU5
Registrar Emergencia multimodal
Dependencia de llamadas
telefónicas y falta de información
clara (fotos, audio, ubicación)
sobre el incidente vehicular.
CU6
Clasificación y Priorización
Dificultad para identificar
rápidamente la naturaleza del
problema y asignar un nivel de
urgencia adecuado.
CU7
Asignación Inteligente a Taller
Lentitud y falta de criterios claros
para identificar y asignar el
proveedor más adecuado según
cercanía y capacidad.
CU8
Gestionar solicitud en taller
Los talleres no reciben solicitudes
de manera organizada, lo que
impide una evaluación rápida y
una respuesta eficiente.
CU9
Seguimiento en tiempo real
Ausencia de trazabilidad del
servicio, lo que genera
incertidumbre en el cliente sobre
el tiempo de llegada de auxilio.
CU10 Notificaciones Push en Tiempo Real
Falta de comunicación inmediata
entre el sistema, el cliente y el
taller sobre los cambios en el
estado de la atención.
CU11 Actualizar Estado de Servicio
Ausencia de un mecanismo
estructurado para reflejar en
tiempo real el avance de la
atención.
CU12 Procesar Pago del Servicio
Necesidad de registrar y gestionar
de manera segura los pagos
realizados por el cliente
```


### Página 15

```text
CU13 Calificar y Reseñar Servicio
Inexistencia de un medio formal
para que el cliente evalúe la
calidad de la atención recibida,
ayudando a la mejora continua del
servicio.
CU14 Consultar Historial y Métricas
Falta de herramientas para
consultar incidentes anteriores,
trazabilidad del servicio e
indicadores de desempeño que
apoyen la toma de decisiones.
CU15 Supervisar Operaciones Globales
Necesidad de contar con un
control centralizado de las
operaciones del sistema,
permitiendo al administrador
monitorear usuarios, talleres,
incidencias, pagos y rendimientos.

Priorización de Casos de Uso Primer Parcial

ID
Caso de Uso
Prioridad
Riesgo
Actores
Ciclo
CU1
Gestionar Inicio/Cierre
de Sesión
Crítica
Alto
Cliente, Taller,
Administrador
C1
CU2
Gestionar Roles y
Permisos
Crítica
Alto
Administrador
C1
CU3
Registrar Cliente y
Vehículo
Importante
Medio
Cliente
C1
CU4
Registrar Taller y
Técnicos
Importante
Medio
Dueño del Taller,
Administrador
C1
CU5
Registrar Emergencia
Multimodal
Crítica
Alto
Cliente
C2
CU6
Clasificación y
Priorización
Crítica
Alto
Módulo IA
C2
CU7
Gestionar solicitud en
taller
Crítica
Alto
Dueño del Taller,
Técnico
C2
CU8
Gestionar solicitud en
Taller
Crítica
Alto
Dueño del Taller,
Técnico
C2
CU9
Seguimiento en tiempo
real
Crítica
Alto
Cliente, Técnico,
Dueño del Taller
C2
CU10 Notificaciones Push en
Tiempo Real
Importante
Medio
Cliente, Taller,
Administrador
C2
```


### Página 16

```text
CU11 Actualizar Estado del
Servicio
Crítica
Medio
Técnico, del Taller
nomas
C2
CU12 Procesar Pago del
Servicio
Crítica
Alto
Cliente, Sistema
C3
CU13 Calificar y Reseñar
Servicio
Importante
Medio
Cliente
C3
CU14 Consultar Historial y
Métricas
Importante
Baja
Cliente, Taller,
Administrador
C3
CU15 Supervisar
Operaciones Globales
Importante
Medio
Administrador
C3


Tabla de Casos de Uso continuación Segundo Parcial

ID
Nombre del Caso de Uso
Justificación
CU16
Administrar tenants y redes de talleres
Permite incorporar el concepto de
tenant dentro del sistema,
registrando organizaciones o
redes de talleres independientes
que utilizarán la misma
plataforma sin mezclar
información.
CU17
Validar aislamiento de datos por tenant
Garantiza que cada usuario, taller,
incidente, pago y métrica
pertenezca únicamente a su
tenant, evitando que un usuario
pueda visualizar información de
otra organización.
CU18
Registrar emergencia en modo offline
Permite que el cliente registre una
emergencia aun cuando no tenga
conexión estable a internet,
guardando la información en el
dispositivo.
CU19
Sincronizar emergencias pendientes
Permite enviar automáticamente
al backend las emergencias
guardadas localmente cuando se
recupera la conexión, evitando
duplicidad de tenants y
actualizando el estado local.
CU20
Gestionar tracking en vivo mediante
WebSockets
Permite transmitir en tiempo real
la ubicación del técnico o taller
asignado, así como los cambios
reales de estado del incidente
durante la atención.
CU21
Gestionar cotizaciones y selección de
taller
Permite que los talleres generen
cotizaciones del daño, indiquen
tiempo estimado de reparación y
```


### Página 17

```text
que el cliente seleccione el taller
que realizará el servicio.
CU22
Procesar pago mediante pasarela de
pagos
Complementa el pago existente
incorporando una pasarela de
pago, validación de transacción,
confirmación y actualización
automática del estado de pago.
CU23
Visualizar dashboard operacional por
tenant
Permite mostrar indicadores
reales desde la base de datos,
como tiempos promedio,
incidentes por tipo, talleres
eficientes, zonas con más
incidentes, casos cancelados y
cumplimiento SLA.
CU24
Gestionar penalidad por cancelación de
solicitud
Permite aplicar una penalidad
económica cuando el cliente
cancela una solicitud de
emergencia después de que el
taller o técnico ya fue asignado.
CU25
Generar reportes operacionales por
tenant
Permite que el dueño del taller o
administrador genere reportes
operacionales filtrados por tenant,
que permitan analizar el
desempeño operativo.
CU26
Generar cobro de multa por cancelación
de servicio impulsado por IA
Aplica una penalidad por
cancelación de emergencias una
vez que el taller o técnico ha sido
asignado, todo calculado
mediante una IA
CU27
Visualizar Mapa de Calor de Incidentes
por zona
Permite al dueño del taller o al
administrador del sistema
visualizar en un mapa interactivo
las zonas con mayor
concentración de incidentes
vehiculares registrados en la
plataforma


3.1.2 Priorizar Casos de Uso

ID
Caso de Uso
Estado
Prioridad
Riesgo
Actores
Ciclo
CU16 Administrar
tenants y redes
de talleres
Incluido
Crítica
Alto
Administrador
C4
CU17 Validar
aislamiento de
datos por tenant
Incluido
Crítica
Alto
Sistema,
Administrador
C4
CU18 Registrar
emergencia en
modo offline
Incluido
Crítica
Alto
Cliente
C4
CU19 Sincronizar
emergencias
pendientes
Incluido
Crítica
Alto
Cliente, Sistema
C4
```


### Página 18

```text
CU20 Gestionar
tracking en vivo
mediando
WebSockets
Incluido
Crítica
Alto
Cliente,
Técnico, Taller,
Sistema
C4
CU21 Gestionar
cotizaciones y
selección de
taller
Incluido
Crítica
Medio
Cliente, Dueño
del Taller
C5
CU22 Integrar pasarela
de pago
Incluido
Crítica
Alto
Cliente, Sistema
C5
CU23 Visualizar
dashboard
operacional por
tenant.
Incluido
Crítica
Medio
Administrador,
Dueño del
Taller
C5
CU24 Gestionar
penalidad por
cancelación de
solicitud
Incluido
Crítica
Alto
Cliente
C5
CU25 Generar reportes
operacionales
por tenant
Incluido
Crítica
Medio
Administrador,
Dueño del
Taller
C5
CU26 Generar cobro de
multa por
cancelación de
servicio
impulsado por IA
Incluido
Crítica
Medio
Administrador
C5
CU27 Visualizar Mapa
de Calor de
Incidentes por
zona
Incluido
Crítica
Medio
Dueño del
Taller,
Administrador
C5

3.1.3 Detallar Casos de Uso

CICLO #4

CU16. Administrar tenants y redes de talleres


Nombre de CU
Administrar Tenants y Redes de Talleres
Propósito
Permite registrar, modificar y administrar las organizaciones o redes de
talleres que utilizarán la plataforma bajo el modelo SaaS multi-tenant.
Actores
Administrador
```


### Página 19

```text
Actor Principal
Administrador
Precondición
El administrador SaaS debe estar autenticado en el sistema y contar
con permisos de administración global.
Flujo de Trabajo
•
Acceso al módulo de administración de tenants
•
Registro de una nueva organización o red de talleres
•
Ingreso de datos del tenant, estado, responsable y
configuración inicial
•
Asociación de talleres, usuarios e información operativa
•
Almacenamiento del tenant en la base de datos
•
Confirmación de creación o actualización del tenant
Postcondición
Tenant registrado o actualizado correctamente, quedando habilitado
para operar dentro de la plataforma.
Excepción
Datos incompletos, tenant duplicado, usuario sin permisos o error al
registrar la organización.
```


### Página 20

```text
CU17. Validar Aislamiento de Datos por Tenant


Nombre de CU
Validar Aislamiento de Datos por Tenant
Propósito
Garantiza que cada usuario, taller, incidente, pago, cotización y métrica
pertenezca únicamente a su tenant, evitando el acceso a información de
otras organizaciones.
Actores
Sistema, Administrador
Actor Principal
Sistema
Precondición
El usuario debe estar autenticado y asociado a un tenant válido dentro
de la plataforma.
Flujo de Trabajo
•
El usuario inicia sesión en la plataforma.
•
El sistema identifica el tenant asociado al usuario autenticado.
•
Se aplica el filtro de tenant en las consultas al backend.
•
El sistema recupera únicamente los datos pertenecientes al
tenant correspondiente
•
Se registra la operación para control y trazabilidad
Postcondición
El usuario visualiza únicamente la información correspondiente a su
tenant.
Excepción
Usuario sin tenant asignado, intento de acceso no autorizado, token
inválido o error en el filtro de información.

CU18. Registrar Emergencia en Modo Offline

Nombre de CU
Registrar Emergencia en Modo Offline
Propósito
Permite al cliente registrar una emergencia vehicular aun cuando no
tenga conexión estable a internet, guardando la información localmente
hasta que pueda ser sincronizada con el backend.
Actores
Cliente/
```


### Página 21

```text
Actor Principal
Cliente
Precondición
El cliente debe estar autenticado previamente en la aplicación móvil o
PWA, y debe existir una pérdida o ausencia de conexión a internet.
Flujo de Trabajo
•
El cliente accede a la opción de registrar emergencia
•
El sistema detecta que no existe conexión a internet
•
El cliente ingresa la información del incidente, ubicación,
descripción y evidencias disponibles
•
La aplicación guarda la emergencia en almacenamiento local
•
El incidente queda marcado como “pendiente de
sincronización”
•
El sistema muestra al usuario que la emergencia aún no fue
enviada al servidor
Postcondición
Emergencia almacenada localmente y marcada como pendiente de
sincronización.
Excepción
Error al guardar la información local, datos incompletos, falta de
permisos de ubicación o almacenamiento insuficiente en el dispositivo.

CU19. Sincronizar Emergencias Pendientes


Nombre de CU
Sincronizar Emergencias Pendientes
Propósito
Permite enviar automáticamente al backend las emergencias
registradas en modo offline cuando la conexión a internet sea
restablecida, evitando duplicidad de incidentes.
Actores
Cliente, Sistema
Actor Principal
Sistema
Precondición
Debe existir al menos una emergencia almacenada localmente con
estado “pendiente de sincronización” y la conexión a internet debe
haberse restablecido.
Flujo de Trabajo
•
La aplicación detecta la recuperación de conexión
•
El sistema consulta las emergencias pendientes almacenadas
localmente
•
Se valida el identificador local del incidente para evitar
duplicados
•
La emergencia es enviada al backend
•
El backend registra correctamente el incidente en la base de
datos
•
La aplicación actualiza el estado local de la emergencia como
“sincronizada”
•
El usuario recibe confirmación de que la emergencia fue
enviada correctamente
Postcondición
Emergencia sincronizada con el backend y actualizada localmente
como enviada.
```


### Página 22

```text
Excepción
Error de conexión durante la sincronización, incidente duplicado, falla
en el backend o error al actualizar el estado local.

CU20. Gestionar Tracking en Vivo


Nombre de CU
Gestionar Tracking en Vivo mediante WebSockets
Propósito
Permite visualizar en tiempo real la ubicación del técnico o taller
asignado y actualizar automáticamente el estado del incidente durante
la atención de la emergencia.
Actores
Cliente, Técnico, Dueño del Taller, Sistema
Actor Principal
Técnico
Precondición
El incidente debe estar registrado, aceptado por un taller y contar con
un técnico asignado.
Flujo de Trabajo
•
El técnico inicia la atención del incidente
•
La aplicación obtiene la ubicación actual del técnico
•
El sistema establece una conexión WebSocket entre cliente,
taller y backend
•
El técnico envía actualizaciones de ubicación y estado del
servicio
•
El cliente visualiza el avance del técnico y el estado
actualizado del incidente.
•
El sistema registra los cambios en el historial del incidente
Postcondición
Ubicación y estado del servicio actualizados en tiempo real para el
cliente, taller y sistema.
Excepción
Credenciales incorrectas o usuario no registrado
```


### Página 23

```text
CICLO #5
CU21: Gestionar cotizaciones y selección de taller

Nombre de CU
Gestionar cotizaciones y selección de taller
Propósito
Permite que los talleres generen cotizaciones del daño vehicular y que
el cliente seleccione el taller que realizará el servicio, considerando
precio, tiempo estimado de reparación y disponibilidad.
Actores
Cliente, Dueño del Taller
Actor Principal
Cliente
Precondición
El incidente debe estar registrado, clasificado y disponible para ser
evaluado por talleres pertenecientes al tenant correspondiente.
Flujo de Trabajo
•
El cliente registra o consulta una emergencia previamente
generada
•
El dueño del taller revisa la información del incidente,
evidencias y clasificación del daño.
•
El taller genera una cotización con el monto estimado
•
El cliente visualiza las cotizaciones disponibles
•
El cliente compara precio, tiempo estimado y datos del taller
•
El cliente selecciona el taller que realizará el servicio
•
El sistema registra la selección y actualiza el estado del
incidente
Postcondición
Cotización seleccionada correctamente y taller confirmado para
realizar el servicio.
Excepción
No existen cotizaciones disponibles, taller no disponible, taller no
pertenece al tenant o error al confirmar la selección.

CU22: Integrar pasarela de pago

Nombre de CU
Integrar Pasarela de Pago
```


### Página 24

```text
Propósito
Permite integrar una pasarela de pago para que el cliente efectúe el
pago del servicio de forma digital, registrando la transacción, el estado
de pago y la comisión correspondiente a la plataforma.
Actores
Cliente, Pasarela de Pago
Actor Principal
Cliente
Precondición
El cliente debe tener una cotización seleccionada o un servicio
finalizado con monto definido para realizar el pago.
Flujo de Trabajo
•
El cliente ingresa al módulo de pago del servicio.
•
El sistema muestra el monto total a pagar
•
El cliente selecciona el método de pago disponible
•
La plataforma envía la solicitud de pago a la pasarela
•
La pasarela valida la transacción
•
La plataforma recibe la respuesta de aprobación o rechazo
•
El pago queda registrado en la base de datos
•
El cliente visualiza la confirmación o el rechazo del pago
Postcondición
Pago procesado y registrado correctamente con su estado
correspondiente.
Excepción
Pago rechazado, error de comunicación con la pasarela, monto
inválido, transacción duplicada o cancelación del proceso de pago.


CU23: Visualizar dashboard operacional por tenant

Nombre de CU
Visualizar Dashboard Operacional por Tenant
Propósito
Permite visualizar indicadores operacionales calculados a partir de
datos reales registrados en la base de datos, mostrando únicamente la
información correspondiente al tenant autenticado.
Actores
Administrador del Sistema, Dueño del Taller
Actor Principal
Dueño del Taller
Precondición
El usuario debe estar autenticado, pertenecer a un tenant válido y
contar con permisos para consultar indicadores operacionales.
Flujo de Trabajo
•
El usuario accede al dashboard operacional
•
El sistema identifica el tenant del usuario autenticado
•
El backend consulta métricas
•
El sistema calcula KPIs
•
El dashboard presenta los indicadores mediante tarjetas,
gráficos y tablas
•
El usuario puede aplicar filtros
Postcondición
Dashboard cargado correctamente con indicadores reales
correspondientes al tenant del usuario
```


### Página 25

```text
Excepción
No existen datos suficientes, usuario sin permisos, error en el cálculo
de KPIs o intento de consultar información de otro tenant.

CU24: Gestionar Penalidad por Cancelación de Solicitud

Nombre de CU
Gestionar Penalidad por Cancelación de Solicitud
Propósito
Permite aplicar una penalidad económica cuando el cliente cancela una
solicitud de emergencia después de que el taller o técnico ya fue
asignado, o cuando el servicio se encuentra en una etapa avanzada del
proceso.
Actores
Cliente
Actor Principal
Cliente
Precondición
El cliente debe tener una solicitud de emergencia registrada. La
solicitud debe encontrarse en un estado donde sea posible solicitar la
cancelación, como asignada, en camino o en atención.
Flujo de Trabajo
•
El cliente ingresa al detalle de la emergencia activa
•
El cliente selecciona la poción de cancelar solicitud
•
El sistema verifica el estado actual del incidente y el tiempo
transcurrido
•
El sistema determina si corresponde aplicar una penalidad por
cancelación
•
Si corresponde multa, el sistema calcula el monto de la
penalidad según las reglas establecidas
•
El sistema actualiza el estado del incidente como cancelado
con penalidad o cancelado sin penalidad
•
El sistema registra la acción en la bitácora y notifica al cliente
el resultado de la cancelación
Postcondición
La solicitud queda cancelada correctamente. En caso de corresponder,
la penalidad queda registrada y asociada al cliente, al incidente y al
estado de pago correspondiente
Excepción
Solicitud inexistente, incidente ya finalizado, usuario sin permisos,
solicitud perteneciente a otro tenant, error al registrar el cobro o fallo
en la comunicación con la pasarela de pago
```


### Página 26

```text
CU25: Generar Reportes Operacionales por Tenant

Nombre de CU
Generar Reportes Operacionales por Tenant
Propósito
Permite generar reportes operacionales filtrados por tenant, rango de
fechas, taller, tipo de incidente, estado del servicio o técnico asignado.
El objetivo es producir información formal y exportable para analizar
el rendimiento operativo.
Actores
Dueño del Taller, Administrador
Actor Principal
Dueño del Taller
Precondición
El usuario debe estar autenticado, pertenecer a un tenant válido y
contar con permisos para generar reportes operacionales. Además,
deben existir datos registrados de incidentes, talleres, asignaciones,
pagos o métricas dentro del periodo seleccionado.
Flujo de Trabajo
•
El usuario ingresa al módulo de reportes operacionales
•
El sistema identifica el tenant del usuario autenticado
•
El usuario selecciona los filtros del reporte
•
El sistema consulta los datos operacionales correspondientes al
tenant
•
El sistema procesa la información y genera el reporte con
métricas relevantes
•
El usuario selecciona el formato de exportación
•
El sistema genera el archivo solicitado y lo deja disponible
para descarga
•
El sistema registra la acción de generación del reporte para
fines de trazabilidad
Postcondición
Reporte operacional generado correctamente y disponible para
descarga, mostrando únicamente información correspondiente al tenant
del usuario autenticado.
Excepción
Usuario sin permisos, tenant inválido, rango de fechas incorrecto,
ausencia de datos para los filtros seleccionados, error al consultar la
información o fallo al generar el archivo exportable.
```


### Página 27

```text
3.1.4 Prototipar la Interfaz de Usuario
CU16: Administrar tenants y redes de talleres.- Permite al Administrador del Sistema registrar y gestionar las
organizaciones o redes de talleres que usarán la plataforma. Desde esta interfaz de podría crear un tenant,
modificar sus datos principales, activar o desactivar su operación, etc.


CU17: Validar aislamiento de datos por tenant.- Permite asegurar que cada usuario visualice únicamente la
información correspondiente a su propia organización o red de talleres. Esta funcionalidad es esencial para
cumplir con el enfoque SaaS multi-tenant.
```


### Página 28

```text
CU18: Registrar emergencia en modo offline.- Permite que el cliente registre una emergencia vehicular aun
cuando no tenga conexión a internet. Esto evita que el usuario pierda la solicitud cuando se encuentre en una
zona sin cobertura o con conexión inestable.


CU19: Sincronizar emergencias pendientes.- Permite que las emergencias registradas sin conexión sean
enviadas automáticamente al backend cuando la conexión a internet sea restablecida. El sistema debe evitar
duplicar incidentes y actualizar el estado local de la solitud.
```


### Página 29

```text
CU20: Gestionar tracking en vivo.- Permite que el cliente, dueño del taller y el técnico visualicen
actualizaciones en vivo durante la atención de una emergencia. Esta funcionalidad se implementa mediante
websockets para mantener una comunicación en tiempo real entre los usuarios y el sistema.
```


### Página 30

```text
CICLO #5
CU21: Gestionar Cotizaciones y Selección de Taller.- Permite que el cliente visualice las cotizaciones
generadas por los talleres para la reparación o atención del vehículo. El cliente podrá comparar las opciones
disponibles y seleccionar el taller que considere más conveniente para realizar la atención.

CU22: Integrar Pasarela de Pago.- Permite que el cliente realice el pago del servicio mediante una pasarela de
pagos digital. Esta funcionalidad permite completar el flujo económico del servicio, registrando el pago y
actualizando su estado dentro de la plataforma.

CU23: Visualizar Dashboard Operacional por Tenant.- Permite que el Administrador del Sistema o el
Dueño del Taller visualicen un panel de indicadores operacionales basado en datos reales registrados en la
plataforma. Además, la información será filtrada por según el tenant autenticado, evitando que una organización
visualice datos de otra.
```


### Página 31

```text
CU24: Gestionar Penalidad por Cancelación de Solicitud.- Permite aplicar una penalidad económica cuando
el cliente cancela una solicitud de emergencia después de que el taller o técnico ya fue asignado, o cuando el
servicio se encuentra en una etapa avanzada del proceso. El sistema evalúa el estado actual del incidente, el
tiempo transcurrido y las reglas de negocio configuradas para determinar si corresponde aplicar una multa.

CU25: Generar Reportes Operacionales por Tenant.- Permite generar reportes operacionales filtrados por
tenant, rango de fechas, taller, tipo de incidente, estado del servicio o técnico asignado. El objetivo es producir
información formal y exportable para analizar el rendimiento operativo, los incidentes atendidos, los casos
cancelados, los tiempos de atención, los pagos registrados y el cumplimiento de indicadores del servicio.
```


### Página 32

```text
3.1.5 Estructurar Modelos de Casos de Uso

CICLO #4


CICLO #5
```


### Página 33

```text
3.2 Análisis
3.2.1 Análisis de Arquitectura
3.2.1.1 Identificar Paquetes

PAQUETE
DESCRIPCIÓN
Encargado de administrar los tenants u
organizaciones que utilizarán la plataforma,
permitiendo registrar redes de talleres,
asociar usuarios, talleres, incidentes y
métricas a un tenant específico. Este paquete
garantiza que la plataforma pueda operar
bajo un modelo SaaS.
Responsable de aplicar las reglas de acceso y
filtrado de información según el tenant
autenticado. Este paquete asegura que un
cliente, dueño de taller, técnico o
administrador visualice únicamente los datos
correspondientes a su organización.
Encargado de permitir el registro de
emergencias cuando el usuario no tenga
conexión a internet. Este paquete gestiona el
almacenamiento local de incidentes, el
marcado de solicitudes como pendientes de
sincronización, la sincronización automática
al recuperar la conexión.
Responsable de gestionar la comunicación en
vivo mediante WebSockets, permitiendo
actualizar automáticamente la ubicación del
técnico o taller asignado, los estados del
incidente y las notificaciones inmediatas
durante la atención de la emergencia.
Encargado de calcular y visualizar
indicadores operacionales a partir de datos
reales registrados en la base de datos. Este
paquete permite generar dashboards por
tenants con métricas.
Este paquete se relaciona con los casos de
uso encargados de gestionar cotizaciones del
daño vehicular, selección de taller, tiempo
estimado de reparación y pago mediante
pasarela de pagos. Permite completar el flujo
económico y operativo del servicio.
```


### Página 34

```text
3.2.1.2 Relacionar Paquetes y Casos de Uso

Paquete de Gestión Multi-Tenant

Paquete de Seguridad y Aislamiento de Datos

Paquete de Modo offline y Sincronización

Paquete de Tracking en Tiempo Real
```


### Página 35

```text
Paquete de Analítica Operacional y KPIs

Paquete de Cotizaciones y Pagos


3.2.1.3 Vista de Paquetes

Paquete de Gestión Multi-Tenant
```


### Página 36

```text
Paquete de Seguridad y Aislamiento de Datos

Paquete de Modo offline y Sincronización

Paquete de Tracking en Tiempo Real
```


### Página 37

```text
Paquete de Analítica Operacional y KPIs

Paquete de Cotizaciones y Pagos
```


### Página 38

```text
3.2.2 Diagramas de Comunicación
CICLO #4
CU16.- Administrar Tenants y Redes de Talleres

CU17.- Validar Aislamiento de Datos por Tenant

CU18.- Registrar Emergencia en Modo Offline

CU19.- Sincronizar Emergencias Pendientes

CU20.- Gestionar Tracking en Vivo
```


### Página 39

```text
CICLO #5
CU21.- Gestionar cotizaciones y selección de taller

CU22.- Integrar pasarela de pagos

CU23.- Visualizar dashboard operacional por tenant
```


### Página 40

```text
CU24.- Gestionar Penalidad por Cancelación de Solicitud
```


### Página 41

```text
CU25.- Generar Reportes Operacionales por Tenant

3.2.3 Analizar una clase
CICLO #4
CU16 Administrar Tenants y Redes de Talleres
```


### Página 42

```text
CU17 Asignar Usuarios y Sucursales a un Tenant

CU18 Registrar Emergencia en Modo Offline

CU19 Sincronizar Emergencias Pendientes

CU20 Gestionar Tracking en Vivo
```


### Página 43

```text
CU21 Gestionar Cotizaciones y selección de taller

CU22 Integrar Pasarela de Pago
```


### Página 44

```text
CU23 Visualizar Dashboard Operacional por Tenant

CU24 Gestionar Penalidad por Cancelación de Solicitud
```


### Página 45

```text
CU25 Generar Reportes Operacionales por Tenant
```


### Página 46

```text
3.2.4 Analizar un Paquete
```


### Página 47

```text
3.3 Diseño
3.3.1 Diseño de Arquitectura

Arquitectura Física (Diagrama de Despliegue)
```


### Página 48

```text
Arquitectura Lógica (Diagrama de Paquetes)


3.3.2 Diseño de Datos
3.3.2.1 Diseño de Datos Lógicos
 Diagrama de Clases
```


### Página 49

```text
[Página sin texto extraíble; contiene principalmente diagramas o imágenes.]
```


### Página 50

```text
Mapeo
```


### Página 51

```text
[Página sin texto extraíble; contiene principalmente diagramas o imágenes.]
```


### Página 52

```text
Normalización
El sistema de información ya se encuentra en 1ra, 2da, 3ra y 4ta forma normal.

Diagrama Relacional


Tablas de Volumen
1. Tabla: ROL

Campo
Tipo
Tamaño (Bytes)
nro_rol
SERIAL
4
nombre_rol
VARCHAR(100) 100
descripcion
VARCHAR(255) 255
fecha_registro
TIMESTAMP
8

2. Tabla: PERSONA
```


### Página 53

```text
Campo
Tipo
Tamaño (Bytes)
ci
VARCHAR(20)
20
nombre_completo
VARCHAR(150)
150
telefono
VARCHAR(20)
20
correo
VARCHAR(100)
100
direccion
VARCHAR(255)
255
fecha_registro
TIMESTAMP
8

3. Tabla: USUARIO

Campo
Tipo
Tamaño (Bytes)
nro_usuario
SERIAL
4
nombre_usuario
VARCHAR(100)
100
password_hash
VARCHAR(255)
255
estado
VARCHAR(50)
50
fecha_registro
TIMESTAMP
8
ci
VARCHAR(20)
20
nro_rol
INTEGER
4
```


### Página 54

```text
4. Tabla: BITACORA

Campo
Tipo
Tamaño (Bytes)
nro_bitacora
SERIAL
4
accion
VARCHAR(255)
255
fecha_hora
TIMESTAMP
8
nro_usuario
INTEGER
4

5. Tabla: VEHICULO

Campo
Tipo
Tamaño (Bytes)
nro_vehiculo
SERIAL
4
placa
VARCHAR(20)
20
marca_modelo
VARCHAR(100) 100
año
INTEGER
4
fecha_registro
TIMESTAMP
8
nro_usuario
INTEGER
4

6. Tabla: EMPRESA

Campo
Tipo
Tamaño (Bytes)
id_empresa
SERIAL
4
nombre_empresa
VARCHAR(150)
150
estado
VARCHAR(50)
50
```


### Página 55

```text
7. Tabla: TALLER

Campo
Tipo
Tamaño (Bytes)
nro_taller
SERIAL
4
nombre_taller
VARCHAR(150)
150
direccion_escrita
VARCHAR(255)
255
latitud
DECIMAL(10,7)
8
longitud
DECIMAL(10,7)
8
disponibilidad
BOOLEAN
1
fecha_registro
TIMESTAMP
8
id_empresa
INTEGER
4

8. Tabla: SERVICIO_TALLER

Campo
Tipo
Tamaño (Bytes)
nro_servicio
SERIAL
4
nro_taller
INTEGER
4
nombre_servicio
VARCHAR(150) 150
descripcion
TEXT
200
fecha_registro
TIMESTAMP
8
```


### Página 56

```text
9. Tabla: EMERGENCIA

Campo
Tipo
Tamaño (Bytes)
nro_emergencia
SERIAL
4
tipo_emergencia
VARCHAR(100) 100
latitud
DECIMAL(10,7)
8
longitud
DECIMAL(10,7)
8
fecha_inicio
TIMESTAMP
8
fecha_fin
TIMESTAMP
8
estado
VARCHAR(50)
50
prioridad
VARCHAR(50)
50
nro_usuario
INTEGER
4
nro_taller
INTEGER
4

10. Tabla: NOTIFICACION

Campo
Tipo
Tamaño (Bytes)
id_notificacion
SERIAL
4
titulo
VARCHAR(150)
150
cuerpo
TEXT
200
tipo_referencia
VARCHAR(100)
100
leido
BOOLEAN
1
fecha_creacion
TIMESTAMP
8
nro_usuario
INTEGER
4
nro_emergencia
INTEGER
4
```


### Página 57

```text
11. Tabla: MENSAJE

Campo
Tipo
Tamaño (Bytes)
nro_mensaje
SERIAL
4
contenido
TEXT
200
fecha_hora
TIMESTAMP 8
leido
BOOLEAN
1
nro_emergencia
INTEGER
4
nro_usuario
INTEGER
4

12. Tabla: EVIDENCIA

Campo
Tipo
Tamaño (Bytes)
nro_evidencia
SERIAL
4
tipo_archivo
VARCHAR(50)
50
url_archivo
VARCHAR(500)
500
transcripcion_archivo
TEXT
500
diagnostico_archivo
TEXT
500
fecha_carga
TIMESTAMP
8
nro_emergencia
INTEGER
4

13. Tabla: EVALUACION

Campo
Tipo
Tamaño (Bytes)
id_evaluacion
SERIAL
4
puntuacion
INTEGER
4
comentario
TEXT
200
fecha_evaluacion
TIMESTAMP 8
nro_emergencia
INTEGER
4
```


### Página 58

```text
14. Tabla: CONCEPTO_TARIFA

Campo
Tipo
Tamaño (Bytes)
id_concepto
SERIAL
4
nombre_concepto
VARCHAR(150)
150
precio_base
DECIMAL(10,2)
8
tipo
VARCHAR(50)
50

15. Tabla: ORDEN_COBRO

Campo
Tipo
Tamaño (Bytes)
id_orden
SERIAL
4
fecha_emision
TIMESTAMP
8
monto_total
DECIMAL(10,2)
8
estado_cobro
VARCHAR(50)
50
nro_emergencia
INTEGER
4
id_empresa
INTEGER
4

16. Tabla: DETALLE_COBRO

Campo
Tipo
Tamaño (Bytes)
nro_detalle
SERIAL
4
cantidad
INTEGER
4
subtotal
DECIMAL(10,2)
8
id_orden
INTEGER
4
id_concepto INTEGER
4
```


### Página 59

```text
17. Tabla: PAGO

Campo
Tipo
Tamaño (Bytes)
id_pago
SERIAL
4
monto_pagado
DECIMAL(10,2)
8
metodo_pago
VARCHAR(50)
50
fecha_pago
TIMESTAMP
8
id_orden
INTEGER
4

SCRIPT
-- =============================================
-- SCRIPT COMPLETO DE CREACIÓN DE TABLAS
-- Plataforma Inteligente de Atención de Emergencias Vehiculares
-- Incluye CU13 (Sistema de Pagos con QR Manual)
-- Ejecutar en Supabase SQL Editor o DBeaver
-- =============================================

-- 1. Extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- =============================================
-- 2. ENUMS
-- =============================================

CREATE TYPE rol_enum AS ENUM ('CLIENTE', 'TALLER', 'ADMIN');

CREATE TYPE estado_incidente_enum AS ENUM (
    'PENDIENTE', 'EN_PROCESO_IA', 'CLASIFICADO', 'ASIGNADO',
    'EN_CAMINO', 'EN_PROCESO', 'ATENDIDO', 'CANCELADO',
'INCIERTO'
);

CREATE TYPE prioridad_enum AS ENUM ('BAJA', 'MEDIA', 'ALTA');

CREATE TYPE clasificacion_enum AS ENUM (
    'BATERIA', 'LLANTA', 'CHOQUE', 'MOTOR', 'OTROS', 'INCIERTO'
);

CREATE TYPE tipo_evidencia_enum AS ENUM ('IMAGEN', 'AUDIO',
'TEXTO');

CREATE TYPE estado_pago_enum AS ENUM (
    'NO_PAGO', 'PENDIENTE', 'PAGADO', 'RECHAZADO'
);

-- =============================================
-- 3. TABLAS
-- =============================================
```


### Página 60

```text
CREATE TABLE IF NOT EXISTS USUARIOS (
    ID_USUARIO            UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    CORREO_ELECTRONICO    VARCHAR(255) UNIQUE NOT NULL,
    HASH_CONTRASENA       TEXT NOT NULL,
    NOMBRE_COMPLETO       VARCHAR(255) NOT NULL,
    TELEFONO              VARCHAR(20),
    ROL                   rol_enum NOT NULL,
    ACTIVO                BOOLEAN DEFAULT TRUE,
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ACTUALIZACION   TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ELIMINACION     TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS CLIENTES (
    ID_USUARIO UUID PRIMARY KEY REFERENCES USUARIOS(ID_USUARIO)
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TALLERES (
    ID_TALLER             UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_USUARIO            UUID UNIQUE REFERENCES
USUARIOS(ID_USUARIO) ON DELETE CASCADE,
    NOMBRE_NEGOCIO        VARCHAR(255) NOT NULL,
    NIT                   VARCHAR(50) UNIQUE,
    DIRECCION             TEXT,
    TASA_COMISION         DECIMAL(5,2) DEFAULT 10.00,
    ACTIVO                BOOLEAN DEFAULT TRUE,
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ACTUALIZACION   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS TECNICOS (
    ID_TECNICO            UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_TALLER             UUID NOT NULL REFERENCES
TALLERES(ID_TALLER) ON DELETE CASCADE,
    NOMBRE_COMPLETO       VARCHAR(255) NOT NULL,
    TELEFONO              VARCHAR(20),
    DISPONIBLE            BOOLEAN DEFAULT TRUE,
    UBICACION_ACTUAL      GEOGRAPHY(POINT, 4326),
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ACTUALIZACION   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS VEHICULOS (
    ID_VEHICULO           UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_USUARIO_CLIENTE    UUID NOT NULL REFERENCES
USUARIOS(ID_USUARIO) ON DELETE CASCADE,
    MARCA                 VARCHAR(100),
```


### Página 61

```text
MODELO                VARCHAR(100),
    ANIO                  INTEGER,
    PLACA                 VARCHAR(20) UNIQUE,
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ACTUALIZACION   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS INCIDENTES (
    ID_INCIDENTE                       UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_USUARIO_CLIENTE                 UUID NOT NULL REFERENCES
USUARIOS(ID_USUARIO),
    ID_VEHICULO                        UUID REFERENCES
VEHICULOS(ID_VEHICULO),
    UBICACION                          GEOGRAPHY(POINT, 4326)
NOT NULL,
    ESTADO                             estado_incidente_enum NOT
NULL DEFAULT 'PENDIENTE',
    PRIORIDAD                          prioridad_enum NOT NULL
DEFAULT 'MEDIA',
    CLASIFICACION                      clasificacion_enum NOT
NULL DEFAULT 'OTROS',
    RESUMEN_IA                         TEXT,
    TIEMPO_ESTIMADO_LLEGADA_MINUTOS    INTEGER,
    FECHA_CREACION                     TIMESTAMP WITH TIME ZONE
DEFAULT NOW(),
    FECHA_ACTUALIZACION                TIMESTAMP WITH TIME ZONE
DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS EVIDENCIAS (
    ID_EVIDENCIA          UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_INCIDENTE          UUID NOT NULL REFERENCES
INCIDENTES(ID_INCIDENTE) ON DELETE CASCADE,
    TIPO                  tipo_evidencia_enum NOT NULL,
    URL_ARCHIVO           TEXT NOT NULL,
    CLAVE_ARCHIVO         TEXT,
    TEXTO_TRANSCRITO      TEXT,
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS HISTORIAL_INCIDENTES (
    ID_HISTORIAL          UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_INCIDENTE          UUID NOT NULL REFERENCES
INCIDENTES(ID_INCIDENTE) ON DELETE CASCADE,
    ESTADO                estado_incidente_enum NOT NULL,
    NOTAS                 TEXT,
    ID_USUARIO_CAMBIO     UUID REFERENCES USUARIOS(ID_USUARIO),
    FECHA_CAMBIO          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ASIGNACIONES (
```


### Página 62

```text
ID_ASIGNACION         UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_INCIDENTE          UUID UNIQUE REFERENCES
INCIDENTES(ID_INCIDENTE),
    ID_TALLER             UUID REFERENCES TALLERES(ID_TALLER),
    ID_TECNICO            UUID REFERENCES TECNICOS(ID_TECNICO),
    FECHA_ASIGNACION      TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_ACEPTACION      TIMESTAMP WITH TIME ZONE,
    FECHA_RECHAZO         TIMESTAMP WITH TIME ZONE,
    MOTIVO_RECHAZO        TEXT
);

CREATE TABLE IF NOT EXISTS PAGOS (
    ID_PAGO               UUID PRIMARY KEY DEFAULT
gen_random_uuid(),
    ID_INCIDENTE          UUID UNIQUE REFERENCES
INCIDENTES(ID_INCIDENTE),
    ID_USUARIO_CLIENTE    UUID REFERENCES USUARIOS(ID_USUARIO),
    ID_TALLER             UUID REFERENCES TALLERES(ID_TALLER),
    ID_ASIGNACION         UUID REFERENCES
ASIGNACIONES(ID_ASIGNACION),
    MONTO                 DECIMAL(10,2) NOT NULL,
    COMISION_PLATAFORMA   DECIMAL(10,2) NOT NULL,
    ESTADO                estado_pago_enum DEFAULT 'NO_PAGO',
    METODO_PAGO           VARCHAR(50),
    ID_TRANSACCION        VARCHAR(255),
    COMPROBANTE_URL       TEXT,
    COMPROBANTE_CLAVE     TEXT,
    NOTAS_CLIENTE         TEXT,
    FECHA_CREACION        TIMESTAMP WITH TIME ZONE DEFAULT
NOW(),
    FECHA_MARCADO_PAGO    TIMESTAMP WITH TIME ZONE,
    FECHA_CONFIRMACION    TIMESTAMP WITH TIME ZONE,
    FECHA_RECHAZO         TIMESTAMP WITH TIME ZONE,
    MOTIVO_RECHAZO        TEXT,
    ID_USUARIO_CONFIRMO   UUID REFERENCES USUARIOS(ID_USUARIO),
    FECHA_ACTUALIZACION   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 4. ÍNDICES
-- =============================================

CREATE INDEX IF NOT EXISTS idx_pagos_estado ON PAGOS(ESTADO);
CREATE INDEX IF NOT EXISTS idx_pagos_taller ON PAGOS(ID_TALLER);
CREATE INDEX IF NOT EXISTS idx_pagos_cliente ON
PAGOS(ID_USUARIO_CLIENTE);

CREATE INDEX IF NOT EXISTS idx_incidentes_estado ON
INCIDENTES(ESTADO);
CREATE INDEX IF NOT EXISTS idx_incidentes_cliente ON
INCIDENTES(ID_USUARIO_CLIENTE);

CREATE INDEX IF NOT EXISTS idx_asignaciones_taller ON
ASIGNACIONES(ID_TALLER);
```


### Página 63

```text
CREATE INDEX IF NOT EXISTS idx_asignaciones_tecnico ON
ASIGNACIONES(ID_TECNICO);

CREATE INDEX IF NOT EXISTS idx_incidentes_ubicacion ON
INCIDENTES USING GIST(UBICACION);
CREATE INDEX IF NOT EXISTS idx_tecnicos_ubicacion ON TECNICOS
USING GIST(UBICACION_ACTUAL);

-- =============================================
-- FIN DEL SCRIPT
-- =============================================

SELECT 'Schema completo creado correctamente. Listo para usar.'
AS mensaje;
```


### Página 64

```text
3.3.3 Diseño de Caso de Uso

Diagrama de Secuencia
CICLO #4
CU16 Administrar Tenants y Redes de Talleres

CU17 Validar aislamiento de datos por Tenant
```


### Página 65

```text
CU18 Registrar emergencia en modo offline

CU19 Sincronizar emergencias pendientes
```


### Página 66

```text
CU20 Gestionar tracking en vivo

CU21 Gestionar cotizaciones y selección de taller
```


### Página 67

```text
CU22 Integrar pasarela de pago

CU23 Visualizar dashboard operacional por tenant
```


### Página 68

```text
CU24 Gestionar Penalidad por Cancelación de Solicitud

CU25 Generar Reportes Operacionales por Tenant
```


### Página 69

```text
3.3.4 Diagrama de Navegación
CICLO #4

CICLO #5
```


### Página 70

```text
3.3.5 Diagrama de Red
```


### Página 71

```text
3.3.6 Diagrama de Estado
CICLO #4
CU16 Administrar Tenants y Redes de Talleres
```


### Página 72

```text
CU17 Validar Aislamiento de Datos por Tenant
```


### Página 73

```text
CU18 Registrar Emergencia en Modo Offline
```


### Página 74

```text
CU19 Sincronizar Emergencias Pendientes
```


### Página 75

```text
CU20 Gestionar Tracking en Vivo
```


### Página 76

```text
CICLO #5
CU21 Gestionar cotizaciones y selección de taller
```


### Página 77

```text
CU22 Integrar pasarela de pago
```


### Página 78

```text
CU23 Visualizar dashboard operacional por tenant
```


### Página 79

```text
CU24 Gestionar Penalidad por Cancelación de Solicitud
```


### Página 80

```text
CU25 Generar Reportes Operacionales por Tenant
```


### Página 81

```text
3.3.7 Diagrama de Tiempo
CICLO #4
CU16 Administrar Tenants y Redes de Talleres

CU17 Validar Aislamiento por Tenants

CU18 Registrar Emergencia en Modo Offline

CU19 Sincronizar Emergencias Pendientes

CU20 Gestionar Tracking en Vivo
```


### Página 82

```text
CICLO #5
CU21 Gestionar cotizaciones y selección de talleres

CU22 Integrar pasarela de pago

CU23 Visualizar dashboard operacional por tiempo

CU24 Gestionar Penalidad por Cancelación de Solicitud

CU25 Generar Reportes Operacionales por Tenant
```


### Página 83

```text
3.4 Implementación
3.4.1 Elección de Plataforma de Desarrollo de Software
3.4.1.1 Lenguaje de Programación
Para el desarrollo de la Plataforma de Atención de Emergencias Vehiculares, se ha optado por
una arquitectura moderna y distribuida, seleccionando lenguajes y frameworks específicos para
cada entorno con el fin de maximizar el rendimiento y la integración con Inteligencia Artificial:
▪
Backend (Python / FastAPI): Se eligió Python como lenguaje principal para el
servidor debido a su ecosistema robusto y su supremacía en el manejo de modelos de
Inteligencia Artificial (procesamiento de audio e imágenes). Se utilizará FastAPI, un
framework web moderno y de alto rendimiento que soporta programación asíncrona
nativa. Esto es vital para manejar en tiempo real las solicitudes de emergencias, las
notificaciones push y el algoritmo de asignación sin bloquear el servidor. Además, el
soporte nativo de FastAPI para el protocolo WebSockets lo hace la herramienta ideal
para soportar el nuevo módulo de comunicación bidireccional, permitiendo el tracking
GPS del mecánico y el chat en vivo sin latencia.
▪
Aplicación Móvil (Dart / Flutter): Para la aplicación de los clientes (conductores) y
mecánicos, se utilizará Dart junto con el SDK Flutter. Esta elección permite compilar
de forma nativa para Android e iOS desde un único código base. Además, Flutter ofrece
un excelente manejo del hardware del dispositivo, facilitando la captura de coordenadas
GPS en tiempo real y multimedia. Para cumplir con la nueva exigencia de tolerancia a
fallos, Flutter facilita la implementación del "Modo Offline", permitiendo integrar
motores de persistencia local para encolar registros de emergencia sin internet y
sincronizarlos en segundo plano al recuperar la red.
▪
Aplicación Web (Angular): Para el portal de gestión de los talleres y la administración
del sistema, se seleccionó Angular. Este framework basado en TypeScript proporciona
una arquitectura sólida orientada a componentes, ideal para construir paneles de control
(dashboards) complejos y visualizar las métricas analíticas (KPIs) del negocio. Se
aprovecharán las capacidades reactivas de Angular (RxJS) para reflejar los cambios de
estado de las emergencias en tiempo real y soportar la arquitectura de Aplicaciones
Web Progresivas (PWA) para el manejo de sesiones inestables.
3.4.1.2 Base de Datos
Para el sistema de emergencias, se eligió PostgreSQL como Sistema de Gestión de Base de
Datos (SGBD) debido a su alto rendimiento, estabilidad, seguridad y compatibilidad
multiplataforma. PostgreSQL es una base de datos relacional de código abierto ampliamente
reconocida por su fiabilidad y capacidad para manejar operaciones transaccionales complejas de
manera eficiente. Su robustez la convierte en la opción ideal para mantener la integridad de los
datos entre clientes, vehículos, talleres e incidentes.
La interacción con el backend en FastAPI se realizará de forma directa mediante el adaptador
psycopg2, implementando un enfoque de consultas SQL puras centralizadas en la capa de
Repositorios de la arquitectura de 3 capas. Esta decisión técnica otorga un control transaccional
absoluto, maximiza el rendimiento de las peticiones al evitar la sobrecarga de procesamiento de
un ORM pesado, y facilita la inyección precisa de los filtros lógicos de aislamiento (Tenant ID)
que exige la arquitectura SaaS multi-tenant. A continuación, se destacan ventajas clave de
PostgreSQL para este proyecto::
▪
Extensibilidad y Geolocalización (PostGIS): PostgreSQL permite la integración de
extensiones como PostGIS, la cual es fundamental para este proyecto. Facilita el cálculo
```


### Página 84

```text
avanzado de distancias, optimizando el algoritmo del "motor de asignación" para
encontrar el taller adecuado más cercano al incidente geolocalizado del cliente.
▪
Escalabilidad: Es altamente escalable frente a conexiones simultáneas, permitiendo
manejar un gran volumen de registros de emergencias, historiales de atención y
telemetría en tiempo real sin comprometer el rendimiento del sistema durante horas pico
(como días de lluvia o accidentes masivos).
▪
Soporte JSON: PostgreSQL ofrece soporte nativo para el almacenamiento de datos en
formato JSON/JSONB. Esta funcionalidad brinda flexibilidad para guardar las "fichas
estructuradas" y los metadatos dinámicos generados por los módulos de Inteligencia
Artificial (clasificación, transcripción de texto), sin necesidad de alterar el esquema
relacional principal.
▪
Seguridad: Incluye múltiples mecanismos de seguridad, cifrado de contraseñas y
control de acceso por roles. Esto garantiza la confidencialidad de la información
personal de los clientes, la ubicación de sus vehículos y los datos de facturación de los
talleres mecánicos.
3.4.1.3 Sistemas Operativos
Para el sistema de emergencias, se eligió PostgreSQL como Sistema de Gestión de Base de
Datos (SGBD) debido a su alto rendimiento, estabilidad, seguridad y compatibilidad
multiplataforma. PostgreSQL es una base de datos relacional de código abierto ampliamente
reconocida por su fiabilidad y capacidad para manejar operaciones transaccionales complejas de
manera eficiente. Su robustez la convierte en la opción ideal para mantener la integridad de los
datos entre clientes, vehículos, talleres e incidentes.
La interacción con el backend en FastAPI se realizará de forma directa mediante el adaptador
psycopg2, implementando un enfoque de consultas SQL puras centralizadas en la capa de
Repositorios de la arquitectura de 3 capas. Esta decisión técnica otorga un control transaccional
absoluto, maximiza el rendimiento de las peticiones al evitar la sobrecarga de procesamiento de
un ORM pesado, y facilita la inyección precisa de los filtros lógicos de aislamiento (Tenant ID)
que exige la arquitectura SaaS multi-tenant. A continuación, se destacan ventajas clave de
PostgreSQL para este proyecto::
▪
Extensibilidad y Geolocalización (PostGIS): PostgreSQL permite la integración de
extensiones como PostGIS, la cual es fundamental para este proyecto. Facilita el cálculo
avanzado de distancias, optimizando el algoritmo del "motor de asignación" para
encontrar el taller adecuado más cercano al incidente geolocalizado del cliente.
▪
Escalabilidad: Es altamente escalable frente a conexiones simultáneas, permitiendo
manejar un gran volumen de registros de emergencias, historiales de atención y
telemetría en tiempo real sin comprometer el rendimiento del sistema durante horas pico
(como días de lluvia o accidentes masivos).
▪
Soporte JSON: PostgreSQL ofrece soporte nativo para el almacenamiento de datos en
formato JSON/JSONB. Esta funcionalidad brinda flexibilidad para guardar las "fichas
estructuradas" y los metadatos dinámicos generados por los módulos de Inteligencia
Artificial (clasificación, transcripción de texto), sin necesidad de alterar el esquema
relacional principal.
▪
Seguridad: Incluye múltiples mecanismos de seguridad, cifrado de contraseñas y
control de acceso por roles. Esto garantiza la confidencialidad de la información
personal de los clientes, la ubicación de sus vehículos y los datos de facturación de los
talleres mecánicos.
```


### Página 85

```text
3.4.1.4 Otros
▪
Control de Versiones (GitHub): Se designó GitHub como plataforma central para
gestionar el código fuente mediante el sistema de control de versiones Git. Esto
facilitará la organización de las distintas ramas de desarrollo (Backend, Frontend Web,
App Móvil), el seguimiento de problemas (issues) y el mantenimiento de un repositorio
estructurado, vital para la presentación académica y la trazabilidad del código.
▪
Servicios Cloud / IA: Aunque el núcleo lógico reside en FastAPI, el sistema contempla
la integración con servicios externos o librerías especializadas en la nube para el
procesamiento de modelos multimodales de Inteligencia Artificial (conversión de audio
a texto y visión artificial para análisis básico de imágenes).
3.4.2 Arquitectura del Sistema
```


### Página 86

```text
3.4.3 Arquitectura del Subsistema

P1 Gestión de Usuarios y Roles

P2 Seguridad y Administración
```


### Página 87

```text
P3 Roles y Funcionalidades

P4. Gestión Emergencias e IA
```


### Página 88

```text
P5 Atención y Seguimiento Operativo

3.5 Flujo de Trabajo: Pruebas
3.5.1 Planificar Pruebas
La planificación de pruebas establece el marco estratégico, organizativo y de recursos para
llevar a cabo la verificación y validación de la Plataforma Inteligente de Atención de
Emergencias Vehiculares. El objetivo es asegurar que el sistema cumpla con los requisitos
definidos, la calidad técnica esperada y las necesidades del usuario final, antes de su
implementación y despliegue.
Esta planificación considera la validación de todos los componentes del sistema, incluyendo la
aplicación móvil, la aplicación web, el backend, la base de datos y los módulos de inteligencia
artificial, garantizando el correcto funcionamiento integral de la plataforma.
3.5.2 Objetivos de la Prueba
El objetivo principal es asegurar la calidad del software mediante la verificación de que el
sistema cumple con las especificaciones funcionales y no funcionales definidas.
1.- Validar la Funcionalidad: Confirmar que todos los Casos de Uso (CU)
implementados, especialmente el registro de emergencias, el procesamiento inteligente
de incidentes, la asignación automática de talleres, el seguimiento en tiempo real y la
gestión de pagos, se ejecuten correctamente según las especificaciones establecidas.
2. Verificar la Integridad del Sistema: Asegurar que los distintos componentes del
sistema (aplicación móvil en Flutter, aplicación web en Angular, backend en FastAPI,
base de datos PostgreSQL y módulos de inteligencia artificial) interactúen
correctamente y que el flujo de datos se mantenga consistente en todo momento.
3. Asegurar la Usabilidad: Verificar que las interfaces de usuario, tanto en la
aplicación móvil como en la web, sean intuitivas, eficientes y permitan al usuario
reportar emergencias y hacer seguimiento del servicio de manera sencilla.
4. Validar el Procesamiento Inteligente: Confirmar que los módulos de inteligencia
artificial funcionen correctamente en tareas como la transcripción de audio,
clasificación de incidentes, análisis de imágenes y generación automática de resúmenes.
```


### Página 89

```text
5. Detectar Defectos: Identificar y documentar errores o desviaciones en el
comportamiento esperado del sistema en etapas tempranas, facilitando su corrección
antes de la implementación final.
3.5.3 Estrategia de Pruebas

Tipo de Prueba
Descripción
Enfoque
Pruebas de Unidad
Verificar el funcionamiento del
código fuente de componentes
individuales
Caja blanca. Se enfoca en la
lógica del Backend y las
operaciones de la Base de
Datos
Pruebas de
Integración
Comprobar la interacción y
comunicación correcta entre los
paquetes.
Se valida el flujo completo de
un CU.
Pruebas de
Validación
Asegurar que el sistema cumple
con los requisitos funcionales
desde la perspectiva del usuario.
Caja negra. Se utilizan los
Casos de Prueba definidos
para verificar la
entrada/resultado esperado.
Pruebas de
Aceptación
Obtener la aprobación formal del
cliente o usuario clave sobre la
idoneidad del sistema para su uso
operativo.
Se ejecutan los casos de
prueba de alta prioridad en el
ambiente de prueba para
simular el uso real.
```


### Página 90

```text
3.5.4 Casos de Pruebas (Implementar Pruebas)
CICLO #4
CU16 Administrar Tenants y Redes de Talleres
Campo
Descripción
Caso de uso
Administrar Tenants y Redes de Talleres
Descripción
Permite al Administrador del sistema registrar, modificar y administrar
tenants o redes de talleres dentro de la plataforma, asociando usuarios,
talleres e información operativa a una organización específica
Precondiciones Administrador autenticado con permisos de administración del sistema.

Paso
Acción
Resultado esperado
Estado
1
Ingresar al módulo de
administración de tenants
Se muestra la pantalla de gestión de
tenants

Satisfactorio
2
Registrar los datos de una
nueva red de talleres

El sistema valida la información
ingresada
Satisfactorio
3
Asociar usuarios y talleres al
tenant
Usuarios y talleres quedan vinculados
al tenant correspondiente
Satisfactorio
4
Guardar la configuración del
tenant
El tenant queda registrado en la base
de datos
Satisfactorio
5
Visualizar confirmación de
registro
Se muestra mensaje de operación
exitosa
Satisfactorio

Responsable
Administrador del Sistema
Resultado de la prueba Satisfactorio
Adjunto
```


### Página 91

```text
CU17 Validar Aislamiento de Datos por Tenant
Campo
Descripción
Caso de uso
Validar Aislamiento de Datos por Tenant
Descripción
Permite garantizar que cada usuario visualice únicamente la información
correspondiente a su tenant, evitando el acceso a datos de otras
organizaciones o redes de talleres.
Precondiciones Usuario autenticado y asociado correctamente a un tenant válido.

Paso
Acción
Resultado esperado
Estado
1
Iniciar sesión con un usuario
perteneciente a un tenant
El sistema identifica el tenant del
usuario autenticado
Satisfactorio
2
Solicitar información desde la
plataforma
El backend aplica el filtro por
tenant
Satisfactorio
3
Consultar incidentes, talleres o
métricas
Se muestran solo los datos del
tenant correspondiente
Satisfactorio
4
Intentar acceder a datos de otro
tenant
El sistema bloquea el acceso no
autorizado
Satisfactorio
5
Mostrar información autorizada
El usuario visualiza únicamente
los datos permitidos
Satisfactorio

Responsable
Cliente, Dueño del Taller, Técnico y Administrador del Sistema
Resultado de la
prueba
Satisfactorio
Adjunto
```


### Página 92

```text
CU18 Registrar Emergencia en Modo Offline
Campo
Descripción
Caso de uso
Registrar Emergencia en Modo Offline
Descripción
Permite al cliente registrar una emergencia vehicular aunque no tenga
conexión a internet, guardando la información de forma local y
marcándola como pendiente de sincronización.
Precondiciones Cliente autenticado previamente en la aplicación móvil o PWA y sin
conexión estable a internet.

Paso
Acción
Resultado esperado
Estado
1
Abrir la opción de registrar
emergencia
Se muestra el formulario de
emergencia
Satisfactorio
2
Detectar ausencia de conexión a
internet
El sistema activa el modo offline
Satisfactorio
3
Ingresar datos de la emergencia,
ubicación y evidencias
La información es capturada
correctamente
Satisfactorio
4
Guardar la emergencia
localmente
La emergencia queda almacenada
en el dispositivo
Satisfactorio
5
Marcar emergencia como
pendiente de sincronización
El usuario visualiza el estado
“pendiente de sincronización”
Satisfactorio

Responsable
Cliente
Resultado de la
prueba
Satisfactorio
Adjunto
```


### Página 93

```text
CU19 Sincronizar Emergencias Pendientes
Campo
Descripción
Caso de uso
Sincronizar Emergencias Pendientes
Descripción
Permite sincronizar automáticamente las emergencias registradas en modo
offline cuando la conexión a internet sea restablecida, evitando duplicar
incidentes y actualizando el estado local de la solicitud.
Precondiciones Existencia de una emergencia guardada localmente con estado pendiente
de sincronización y conexión a internet restablecida.

Paso
Acción
Resultado esperado
Estado
1
Recuperar conexión a internet
La aplicación detecta la conexión
restablecida
Satisfactorio
2
Consultar emergencias pendientes
en almacenamiento local
Se obtiene la lista de
emergencias pendientes
Satisfactorio
3
Enviar emergencia pendiente al
backend
El sistema valida que no exista
duplicidad
Satisfactorio
4
Registrar incidente en la base de
datos principal
El backend registra
correctamente la emergencia
Satisfactorio
5
Actualizar estado local de la
emergencia
La emergencia cambia de
“pendiente” a “sincronizada”
Satisfactorio

Responsable
Cliente
Resultado de la
prueba
Satisfactorio
Adjunto
```


### Página 94

```text
CU20 Gestionar Tracking en Vivo
Campo
Descripción
Caso de uso
Gestionar Tracking en Vivo mediante WebSockets
Descripción
Permite visualizar en tiempo real la ubicación del técnico asignado y el
estado actualizado del incidente mediante una conexión WebSocket entre
cliente, taller y sistema.
Precondiciones Emergencia registrada, taller asignado, solicitud aceptada y técnico
asignado al servicio.

Paso
Acción
Resultado esperado
Estado
1
Abrir la pantalla de
seguimiento de emergencia
Se muestra la pantalla de tracking del
servicio
Satisfactorio
2
Iniciar conexión WebSocket
Se establece comunicación en tiempo
real
Satisfactorio
3
Enviar ubicación actual del
técnico
La ubicación del técnico se actualiza
automáticamente
Satisfactorio
4
Cambiar estado del servicio
Cliente y dueño del taller visualizan el
nuevo estado
Satisfactorio
5
Finalizar el servicio
Se muestra el servicio como finalizado
y se cierra el tracking
Satisfactorio


Responsable
Técnico, Cliente, Dueño del Taller
Resultado
de la prueba
Satisfactorio
Adjunto
```


### Página 95

```text
CICLO #5
CU21 Gestionar cotizaciones y selección de taller
Campo
Descripción
Caso de uso
Gestionar Cotizaciones y Selección de Taller
Descripción
Permite que el cliente visualice las cotizaciones generadas por talleres,
compare precio, tiempo estimado y disponibilidad y seleccione el taller
que realizará la atención del servicio.
Precondiciones Incidente registrado, clasificado y disponible para cotización. El cliente y
el dueño del taller deben estar autenticados y asociados a un tenant válido.

Paso
Acción
Resultado esperado
Estado
1
El cliente solicita cotizaciones
para un incidente registrado
El sistema muestra el detalle del
incidente y habilita la recepción de
respuesta
Satisfactorio
2
El dueño del taller registra una
cotización con monto y tiempo
estimado
La cotización queda registrada y
asociada al incidente y al taller
correspondiente
Satisfactorio
3
El cliente consulta las
cotizaciones disponibles
El sistema muestra las cotizaciones
filtradas según el tenant del usuario
Satisfactorio
4
El cliente compara las
propuestas recibidas
Se visualizan datos como taller,
monto estimado, tiempo aproximado
Satisfactorio
5
El cliente selecciona el taller
preferido
El sistema registra la asignación del
taller y actualiza el estado del
incidente.
Satisfactorio


Responsable
Cliente, Dueño del Taller
Resultado de la prueba Satisfactorio
```


### Página 96

```text
Adjunto
```


### Página 97

```text
CU22 Integrar pasarela de pagos
Campo
Descripción
Caso de uso
Integrar Pasarela de Pagos
Descripción
Permite que el cliente realice el pago del servicio mediante una pasarela
digital, registrando el comprobante, el estado del pago y la confirmación
correspondiente dentro de la plataforma.
Precondiciones El cliente debe tener una cotización seleccionada o un servicio con monto
definido. Debe existir un pago pendiente asociado al servicio.

Paso
Acción
Resultado esperado
Estado
1
El cliente ingresa al módulo de
pago del servicio
El sistema muestra el resumen del
cobro y el estado actual del pago
Satisfactorio
2
El cliente selecciona el método
de pago o registra el
comprobante
El sistema recibe los datos del pago
y valida la información enviada
Satisfactorio
3
El sistema registra el pago como
pendiente de confirmación
El estado del pago cambia a
pendiente y queda asociado al
cliente y al servicio
Satisfactorio
4
El taller o administrador
confirma el pago recibido
El sistema valida el pago y actualiza
su estado como pagado
Satisfactorio
5
El sistema muestra la
confirmación del pago
El cliente visualiza el comprobante o
mensaje de pago confirmado
Satisfactorio

Responsable
Cliente, Dueño del Taller, Administrador
Resultado de
la prueba
Satisfactorio
Adjunto
```


### Página 98

```text
CU23 Generar con IA dashboard operacional por tenant
Campo
Descripción
Caso de uso
Generar con IA dashboard operacional por tenant
Descripción
Permite que el dueño del taller o el administrador del sistema visualice
indicadores operacionales calculados a partir de datos reales, filtrados
según el tenant correspondiente.
Precondiciones Usuario autenticado, asociado a un tenant válido y con permisos para
consultar indicadores operacionales. Deben existir datos registrados de
incidentes, talleres, asignaciones o pagos.

Paso
Acción
Resultado esperado
Estado
1
El usuario accede al dashboard
operacional
El sistema muestra la pantalla
principal del dashboard
Satisfactorio
2
El usuario selecciona filtros de
consulta como fecha, taller, estado
o tipo de incidente
El sistema captura los filtros
seleccionados correctamente
Satisfactorio
3
El sistema valida el tenant del
usuario autenticado
Se garantiza que la consulta utilice
únicamente datos del tenant
correspondiente
Satisfactorio
4
El sistema consulta datos
operacionales de incidentes,
asignaciones, talleres y pagos
Se recuperan los datos reales
necesarios para calcular los
indicadores
Satisfactorio
5
El sistema calcula y muestra los
KPIs operacionales
El usuario visualiza tarjetas,
gráficos y métricas
Satisfactorio

Responsa
ble
Dueño del Taller y Administrador
Resultado
de la
prueba
Satisfactorio
Adjunto
```


### Página 99

```text
CU24 Generar Penalidad por Cancelación de Solicitud
Campo
Descripción
Caso de uso
Gestionar Penalidad por Cancelación de Solicitud
Descripción
Permite aplicar una penalidad económica cuando el cliente cancela una
solicitud de emergencia después de que el taller o técnico ya fue asignado,
o cuando el servicio se encuentra en una etapa avanzada del proceso. El
sistema evalúa el estado del incidente, el tiempo transcurrido y las reglas
de negocio para determinar si corresponde aplicar multa.
Precondiciones Cliente autenticado, emergencia registrada y solicitud en estado
cancelable. El incidente debe estar asociado al cliente y pertenecer al
tenant correspondiente.

Paso
Acción
Resultado esperado
Estado
1
El cliente ingresa al
detalle de una emergencia
activa
El sistema muestra la información actual
del incidente y la opción de cancelar la
solicitud
Satisfactorio
2
El cliente selecciona la
opción de cancelar
solicitud
El sistema recibe la solicitud de
cancelación
Satisfactorio
3
El sistema valida el estado
actual del incidente
El sistema determina si la solicitud puede
cancelarse y si corresponde penalidad
Satisfactorio
4
El sistema calcula y
registra la penalidad, si
corresponde
La multa queda asociada al cliente, al
incidente y al estado de pago
correspondiente
Satisfactorio
5
El sistema actualiza el
estado del incidente
El incidente queda cancelado con
penalidad o sin penalidad, y se registra la
acción en historial
Satisfactorio
6
El sistema notifica al
cliente el resultado de la
cancelación
El cliente visualiza la confirmación de
cancelación y el detalle de la penalidad
aplicada, si corresponde
Satisfactorio
```


### Página 100

```text
Responsabl
e
Cliente, Administrador del Sistema
Resultado
de la
prueba
Satisfactorio
Adjunto
```


### Página 101

```text
CU25 Generar Reportes Operacionales por Tenant
Campo
Descripción
Caso de uso
Generar Reportes Operacionales por Tenant
Descripción
Permite que el dueño del taller o el administrador del sistema genere
reportes operacionales exportables, filtrados por tenant, rango de fechas,
taller, estado del incidente, tipo de emergencia o formato de salida. El
reporte permite analizar incidentes atendidos, pagos, cancelaciones,
tiempos de atención, rendimiento operativo y cumplimiento de
indicadores.
Precondiciones Usuario autenticado, asociado a un tenant válido y con permisos para
generar reportes. Deben existir datos operacionales registrados de
incidentes, talleres, asignaciones, pagos o métricas dentro del periodo
seleccionado.

Paso
Acción
Resultado esperado
Estado
1
El usuario ingresa al módulo
de reportes operacionales
El sistema muestra el formulario de
generación de reportes
Satisfactorio
2
El usuario selecciona filtros
como rango de fechas, taller,
estado, tipo de incidente y
formato
El sistema captura correctamente los
criterios de generación del reporte
Satisfactorio
3
El sistema valida el tenant y
los permisos del usuario
autenticado
Se garantiza que el reporte utilice
únicamente información del tenant
correspondiente
Satisfactorio
4
El sistema consulta datos
operacionales de incidentes,
asignaciones, talleres y pagos
Se recupera la información real
necesaria para construir el reporte
Satisfactorio
5
El sistema consolida la
información y calcula
métricas operacionales
Se generan indicadores como
incidentes atendidos, tiempos
promedio, pagos registrados,
cancelaciones y rendimiento por taller
Satisfactorio
6
El sistema genera el archivo
en el formato seleccionado
El reporte queda generado
correctamente en PDF, Excel o CSV
Satisfactorio
7
El usuario descarga el reporte
generado
El archivo queda disponible para
descarga y se registra la acción en el
historial
Satisfactorio
```


### Página 102

```text
Responsable
Dueño del Taller y Administrador
Resultado de
la prueba
Satisfactorio
Adjunto

CU26 Generar cobro de multa por cancelación de servicio impulsado por IA
Campo
Descripción
Caso de uso
Generar cobro de multa por cancelación de servicio impulsado por IA
Descripción
Permite generar un cobro de multa cuando un cliente cancela una solicitud
de emergencia vehicular después de que el servicio ya fue asignado,
aceptado o se encuentra en proceso de atención. El sistema evalúa el
estado del incidente, valida las reglas de penalidad, calcula el monto
correspondiente y registra el cobro asociado al cliente y al incidente.
Precondiciones Cliente autenticado, solicitud de emergencia registrada y asociada a un
tenant válido. El incidente debe encontrarse en un estado donde la
cancelación pueda generar multa, como asignado, aceptado, en camino o
en atención.

Paso
Acción
Resultado esperado
Estado
1
El cliente solicita cancelar
una emergencia activa
El sistema recibe la solicitud de
cancelación y muestra el detalle del
incidente
Satisfactorio
2
El sistema valida el estado
actual del incidente
Se determina si la solicitud puede
cancelarse y si corresponde aplicar una
multa
Satisfactorio
3
El sistema calcula el monto
de la multa según las reglas
establecidas
Se obtiene el valor de la penalidad de
acuerdo con el estado del servicio y el
tiempo transcurrido
Satisfactorio
4
El sistema registra la multa
asociada al cliente y al
incidente
La penalidad queda almacenada con su
monto, motivo, fecha y estado
correspondiente
Satisfactorio
```


### Página 103

```text
5
El sistema genera el cobro
pendiente de la multa
Se crea un registro de pago pendiente
asociado a la penalidad por cancelación
Satisfactorio
6
El sistema actualiza el
estado del incidente y
notifica al cliente
El incidente queda cancelado con multa
y el cliente visualiza el cobro generado
Satisfactorio


Responsable
Cliente, Administrador del Sistema
Resultado de
la prueba
Satisfactorio
Adjunto
```


### Página 104

```text
CU27 Visualizar Mapa de Calor de Incidentes por zona
Campo
Descripción
Caso de uso
Visualizar Mapa de Calor de Incidentes por zona
Descripción
Permite al dueño del taller o al administrador del sistema visualizar en un
mapa interactivo las zonas con mayor concentración de incidentes
vehiculares registrados en la plataforma. El sistema representa la
información mediante un mapa de calor, donde la intensidad del color
indica la cantidad de solicitudes reportadas en una ubicación determinada,
facilitando el análisis de zonas críticas, la toma de decisiones operativas y
la distribución estratégica de técnicos o talleres.
Precondiciones Usuario autenticado, asociado a un tenant válido y con permisos para
consultar información geográfica de incidentes. Deben existir incidentes
registrados con datos de ubicación, fecha y estado dentro del periodo
seleccionado.

Paso
Acción
Resultado esperado
Estado
1
El usuario ingresa al módulo de
dashboard o análisis geográfico
El sistema muestra la sección del
mapa de incidentes
Satisfactorio
2
El usuario selecciona filtros
como rango de fechas, estado del
incidente, tipo de emergencia o
tenant
El sistema captura correctamente
los criterios de consulta
Satisfactorio
3
El sistema valida el tenant y los
permisos del usuario autenticado
Se garantiza que el mapa utilice
únicamente información del tenant
correspondiente
Satisfactorio
4
El sistema consulta los
incidentes registrados con
ubicación geográfica
Se recuperan los datos de latitud,
longitud y cantidad de incidentes
por zona
Satisfactorio
5
El sistema genera el mapa de
calor con las zonas de mayor
concentración
El usuario visualiza manchas de
intensidad según la cantidad de
incidentes registrados
Satisfactorio
6
El sistema identifica la zona con
mayor incidencia
Se muestra la zona caliente con el
porcentaje y número de incidentes
correspondientes
Satisfactorio
7
El usuario analiza el mapa para
apoyar la toma de decisiones
operativas
El dueño del taller o administrador
puede identificar zonas críticas y
mejorar la asignación de recursos
Satisfactorio
```


### Página 105

```text
Responsable
Dueño del Taller y Administrador
Resultado de
la prueba
Satisfactorio
Adjunto
```


### Página 106

```text
Conclusión
El desarrollo del proyecto Sistema Inteligente para la Gestión de Emergencias
Vehiculares permitió consolidar una propuesta tecnológica orientada a mejorar la
atención, seguimiento y administración de incidentes vehiculares mediante el uso de
herramientas modernas, arquitectura escalable y procesos correctamente modelados. A
lo largo del proyecto se definieron funcionalidades esenciales para que los clientes
puedan registrar emergencias, recibir atención especializada, visualizar el seguimiento
del servicio y contar con mecanismos de comunicación y notificación en tiempo real.
Asimismo, se incorporaron procesos administrativos para la gestión de usuarios,
talleres, tenants, pagos, reportes e indicadores operacionales, fortaleciendo la visión
integral de la plataforma.
Durante el Ciclo 4, el proyecto incorporó funcionalidades clave relacionadas con la
arquitectura multi-tenant, el registro de emergencias en modo offline, la sincronización
de solicitudes pendientes y el seguimiento en vivo mediante WebSockets. Estas
funcionalidades resultan fundamentales para garantizar disponibilidad, trazabilidad y
continuidad operativa incluso en escenarios donde el usuario no cuenta con conexión
estable a internet. Además, la validación del aislamiento de datos por tenant permite
asegurar que cada organización, red de talleres o usuario acceda únicamente a la
información que le corresponde, reforzando la seguridad y la correcta separación de
datos dentro del sistema.
En el Ciclo 5, se amplió el alcance funcional mediante la gestión de cotizaciones,
selección de talleres, integración de pagos, visualización de dashboards operacionales,
aplicación de penalidades por cancelación y generación de reportes por tenant. Estas
funcionalidades fortalecen el componente económico, analítico y administrativo de la
plataforma, permitiendo no solo atender emergencias, sino también medir el
rendimiento operativo, controlar transacciones, aplicar reglas de negocio y generar
información exportable para la toma de decisiones.
Finalmente, la elaboración de diagramas de casos de uso, comunicación, secuencia,
estado, tiempo, navegación, despliegue y análisis de clases permitió representar de
manera estructurada el comportamiento del sistema desde distintas perspectivas. Esto
contribuye a una mejor comprensión del funcionamiento interno de la plataforma y
facilita futuras etapas de implementación, validación y mantenimiento. En conclusión,
el proyecto presenta una solución integral, escalable y alineada con necesidades reales
de atención vehicular, combinando gestión operativa, automatización, seguridad,
análisis de datos y experiencia de usuario en una misma plataforma
```


### Página 107

```text
Recomendación
Se recomienda continuar el desarrollo del Sistema Inteligente para la Gestión de
Emergencias Vehiculares priorizando la implementación progresiva de los módulos
definidos en los ciclos del proyecto, especialmente aquellos relacionados con la
atención en tiempo real, la arquitectura multi-tenant, la sincronización offline, los pagos
digitales y la generación de reportes operacionales. Para garantizar un crecimiento
ordenado de la plataforma, es importante mantener una arquitectura modular, donde
cada funcionalidad se encuentre separada por responsabilidades claras, facilitando el
mantenimiento, la escalabilidad y la incorporación de nuevas características en futuras
versiones.
Asimismo, se recomienda reforzar los mecanismos de seguridad y control de acceso,
principalmente en la validación del aislamiento de datos por tenant, debido a que la
plataforma manejará información sensible de clientes, talleres, incidentes, pagos y
reportes. Cada consulta, operación administrativa o generación de información debe
respetar estrictamente el tenant del usuario autenticado, evitando accesos no autorizados
y garantizando la confidencialidad de los datos.
También es conveniente validar los flujos críticos mediante pruebas funcionales y de
integración, especialmente en casos como el registro de emergencias offline, la
sincronización de solicitudes pendientes, el tracking mediante WebSockets, la selección
de talleres, la aplicación de penalidades y la confirmación de pagos. Estos procesos
impactan directamente en la experiencia del usuario y en la confiabilidad operativa del
sistema.
Finalmente, se recomienda complementar la plataforma con métricas de monitoreo,
auditoría y trazabilidad, de modo que los administradores y dueños de talleres puedan
analizar el desempeño del servicio, identificar cuellos de botella, evaluar tiempos de
respuesta y tomar decisiones basadas en datos reales. La correcta documentación de los
casos de uso, diagramas y pruebas debe mantenerse actualizada conforme evolucione el
sistema, ya que constituye una base fundamental para la implementación, validación y
mejora continua del proyecto.
```


### Página 108

```text
Bibliografía
Fielding, R. T. (2000). Architectural styles and the design of network-based
software  architectures (Tesis doctoral). University of California, Irvine.
Kleppmann, M. (2017). Designing data-intensive applications. O’Reilly Media.
Kurose, J. F., & Ross, K. W. (2021). Computer networking: A top-down approach (8.ª
ed.). Pearson.
Martin, R. C. (2018). Clean architecture: A craftsman’s guide to software structure and
design. Prentice Hall.
Mozilla Developer Network. (2024). WebSocket API. MDN Web Docs.

https://developer.mozilla.org
Mozilla Developer Network. (2024). Service Workers API. MDN Web Docs.

https://developer.mozilla.org
Pressman, R. S., & Maxim, B. R. (2020). Ingeniería de software: Un enfoque
práctico  (9.ªed.). McGraw-Hill.
Sommerville, I. (2016). Ingeniería de software (10.ª ed.). Pearson.
W3C. (2021). Service Workers Nightly Specification. World Wide Web
Consortium.    https://www.w3.org/TR/service-workers/

URL y QR
Enlace a Repositorio
https://github.com/DiegoMelgar61/Plataforma-Inteligente-de-Atenci-n-de-Emergencias-
Vehiculares.git
QR Repositorio
```


### Página 109

```text
Enlace a software web
https://plataforma-inteligente-de-atenci-n.vercel.app/map
QR Software web
```

