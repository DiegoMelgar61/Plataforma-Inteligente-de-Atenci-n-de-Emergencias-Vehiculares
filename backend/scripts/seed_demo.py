#!/usr/bin/env python3
"""
Seed de datos multi-tenant para demo (idempotente y repetible).

Puebla la base con varias redes de talleres (tenants), cada una con clientes,
talleres, técnicos, vehículos e incidentes en toda la gama de estados del enum,
incluyendo asignaciones, evidencias, historial, pagos, informes de servicio y
conversaciones de los asistentes de IA.

TODOS los campos que normalmente produce la IA se rellenan a mano con texto
realista escrito acá — NO se llama a ningún servicio de IA.

Uso (desde backend/):
    python scripts/seed_demo.py
    python scripts/seed_demo.py "postgresql://.../db"   # URL explícita opcional

Convención de credenciales (todas con contraseña 12345678):
    Cliente:  nombre@cliente.com
    Técnico:  nombre@tecnico.com
    Taller:   nombre@taller.com

Idempotencia:
    - Los tenants se crean por NOMBRE único (no se duplican).
    - Un tenant que ya tenga usuarios se saltea por completo.
    - Los correos ya existentes nunca se reutilizan.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from geoalchemy2.elements import WKTElement
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hashear_contrasena
from app.modules.assignments.models import ASIGNACIONES
from app.modules.chat.models import CONVERSACIONES, MENSAJES_CHAT
from app.modules.incidents.models import EVIDENCIAS, HISTORIAL_INCIDENTES, INCIDENTES
from app.modules.informes.models import INFORMES_SERVICIO
from app.modules.payments import service as payment_service
from app.modules.payments.models import PAGOS
from app.modules.technicians.models import TECNICOS
from app.modules.tenants.models import Tenant
from app.modules.users.models import CLIENTES, USUARIOS
from app.modules.vehicles.models import VEHICULOS
from app.modules.workshops.models import TALLERES

PASSWORD = "12345678"

# ── Redes de talleres (tenants nuevos) ───────────────────────────────────────
TENANTS = [
    "Red AutoAyuda Santa Cruz",
    "Grúas y Talleres del Oriente",
    "AsistCar Bolivia",
    "MecánicaExpress Cruceña",
]

# Nombres de pila (un solo nombre por correo, en minúsculas, únicos globalmente).
NOMBRES_PILA = [
    "mauricio", "gustavo", "pablo", "javier", "marco", "ernesto", "ruben",
    "nelson", "cristian", "alvaro", "gonzalo", "hugo", "raul", "sergio",
    "fernando", "ricardo", "oscar", "walter", "victor", "ramiro",
    "alejandra", "veronica", "claudia", "natalia", "gabriela", "isabel",
    "carmen", "teresa", "patricia", "jimena", "cecilia", "lorena", "beatriz",
    "daniela", "andrea", "silvia", "rocio", "elena", "marcela", "paola",
]

APELLIDOS = [
    "Andrade", "Sandoval", "Herrera", "Quispe", "Mamani", "Salinas",
    "Suárez", "Melgar", "Chávez", "Vargas", "Montaño", "Pedraza",
    "Torrico", "Vaca", "Arce", "Balcázar", "Peñaranda", "Mercado",
]

NOMBRES_NEGOCIO = [
    "Taller Mecánico Don Pepe", "AutoService San Martín",
    "Mecánica El Progreso", "Taller Automotriz Banzer",
    "AutoCenter Los Pozos", "Servicio Técnico Conavi",
]
DIRECCIONES = [
    "Av. Banzer km 6, Zona Norte", "Calle Sucre #245, Plan 3000",
    "Av. Cristo Redentor #890, Zona Sur", "Radial 27 #156, Zona Este",
    "Av. Paragua #578, Villa 1ro de Mayo", "Calle Murillo #34, Barrio Hamacas",
]
VEHICULOS_DATA = [
    ("Toyota", "Corolla", 2019), ("Chevrolet", "Sail", 2020),
    ("Nissan", "Tiida", 2018), ("Hyundai", "Accent", 2021),
    ("Suzuki", "Swift", 2017), ("Kia", "Sportage", 2022),
    ("Volkswagen", "Gol", 2018), ("Toyota", "Hilux", 2020),
    ("Ford", "EcoSport", 2019), ("Mitsubishi", "L200", 2019),
    ("Chevrolet", "Cruze", 2021), ("Nissan", "Frontier", 2020),
]

# Coordenadas base dentro de Santa Cruz de la Sierra (lat, lng).
BASE_COORDS = [
    (-17.7840, -63.1812), (-17.7950, -63.1650),
    (-17.7720, -63.2010), (-17.8100, -63.1750),
]

# ── Textos de IA precargados (escritos a mano) por clasificación ─────────────
RESUMEN_IA = {
    "BATERIA": "Vehículo sin arranque por descarga total de batería. El cliente reporta que las luces del tablero encienden débilmente. Se recomienda arranque asistido y revisión del alternador.",
    "LLANTA": "Neumático trasero derecho pinchado tras pisar un objeto punzante. El vehículo está detenido en la vía. Requiere cambio de llanta en sitio.",
    "MOTOR": "Falla en motor con pérdida de potencia y humo blanco por el escape. Posible problema en el sistema de refrigeración o junta de culata. Requiere diagnóstico presencial.",
    "CHOQUE": "Colisión frontal leve con daños en el parachoques delantero. El cliente está fuera de peligro. Se evalúa si el vehículo puede circular o requiere grúa.",
    "OTROS": "Falla mecánica no identificada con ruido irregular al acelerar. Se necesita diagnóstico completo del técnico en sitio.",
}
EVIDENCIA_IMAGEN_ANALISIS = {
    "BATERIA": "En la imagen se observan los bornes de la batería con sulfatación leve. El indicador de carga del tablero marca nivel bajo.",
    "LLANTA": "La imagen muestra el neumático trasero derecho completamente desinflado con un corte visible en la banda de rodadura.",
    "MOTOR": "Se aprecia humo blanco saliendo del compartimiento del motor y residuos de refrigerante cerca del radiador.",
    "CHOQUE": "El parachoques delantero presenta hundimiento y fractura del plástico; el faro derecho está desalineado pero íntegro.",
    "OTROS": "La imagen no permite identificar un daño evidente; se requiere inspección física del componente reportado.",
}
EVIDENCIA_AUDIO_TRANSCRIPCION = {
    "BATERIA": "El auto no prende para nada, giro la llave y solo hace un clic. Anoche quedó con las luces encendidas.",
    "LLANTA": "Pisé algo en la avenida y la llanta de atrás se desinfló de golpe, estoy parado a un costado.",
    "MOTOR": "Empezó a salir humo blanco y perdió fuerza, tuve que orillarme porque no avanzaba.",
    "CHOQUE": "Tuve un choque leve de frente, el parachoques quedó dañado pero estoy bien.",
    "OTROS": "El motor hace un ruido raro cuando acelero, no sé bien qué es.",
}
# Contenido del informe de servicio (mismas 6 claves que usa el módulo informes).
INFORME_CONTENIDO = {
    "BATERIA": {
        "resumen_incidente": "El cliente reportó que su vehículo no encendía por batería descargada tras dejar las luces encendidas durante la noche.",
        "diagnostico": "Batería con carga insuficiente (10.9 V en reposo). Bornes con sulfatación leve. Alternador funcionando dentro de parámetros.",
        "trabajo_realizado": "Se realizó arranque asistido con cables, limpieza de bornes y carga de la batería. Se verificó la tensión de carga del alternador (14.2 V).",
        "estado_final": "Vehículo operativo, encendiendo con normalidad al momento de finalizar la atención.",
        "recomendaciones_preventivas": "Evitar dejar luces o accesorios encendidos con el motor apagado. Revisar la batería cada 6 meses.",
        "proximos_pasos": "Se sugiere una revisión del sistema de carga en taller si la batería vuelve a descargarse en las próximas semanas.",
    },
    "LLANTA": {
        "resumen_incidente": "El cliente sufrió un pinchazo en el neumático trasero derecho tras pisar un objeto punzante en la vía.",
        "diagnostico": "Neumático trasero derecho con corte en la banda de rodadura, sin posibilidad de reparación con parche. Llanta de repuesto en buen estado.",
        "trabajo_realizado": "Se cambió el neumático dañado por la llanta de repuesto y se ajustó el torque de las tuercas al valor recomendado.",
        "estado_final": "Vehículo operativo y en condiciones de circular con la llanta de repuesto instalada.",
        "recomendaciones_preventivas": "Reemplazar cuanto antes el neumático dañado y verificar la presión de las cuatro llantas periódicamente.",
        "proximos_pasos": "Acudir a un taller para adquirir e instalar un neumático nuevo y rotar las llantas.",
    },
    "MOTOR": {
        "resumen_incidente": "El vehículo presentó pérdida de potencia y humo blanco por el escape mientras el cliente circulaba.",
        "diagnostico": "Sobrecalentamiento del motor por bajo nivel de refrigerante y posible falla en la junta de culata. Se detectó fuga en la manguera superior del radiador.",
        "trabajo_realizado": "Se dejó enfriar el motor, se repuso refrigerante y se selló temporalmente la fuga. Se recomendó no exigir el motor hasta la reparación de fondo.",
        "estado_final": "Vehículo operativo de forma provisional; requiere reparación mayor en taller.",
        "recomendaciones_preventivas": "No continuar circulando con el testigo de temperatura encendido. Revisar el sistema de refrigeración de inmediato.",
        "proximos_pasos": "Trasladar el vehículo a taller para cambio de manguera, revisión de la junta de culata y prueba de compresión.",
    },
    "CHOQUE": {
        "resumen_incidente": "El cliente tuvo una colisión frontal leve que dañó el parachoques delantero del vehículo.",
        "diagnostico": "Parachoques delantero fracturado y faro derecho desalineado. No se observan daños estructurales ni fugas; el vehículo puede circular con precaución.",
        "trabajo_realizado": "Se aseguraron las piezas sueltas del parachoques y se realineó provisionalmente el faro para permitir la circulación segura.",
        "estado_final": "Vehículo operativo con daños estéticos; apto para circular a baja velocidad.",
        "recomendaciones_preventivas": "Mantener distancia de seguridad. Reparar el parachoques y verificar la alineación en taller.",
        "proximos_pasos": "Llevar el vehículo a chapería y pintura para reemplazo del parachoques y revisión del sistema de luces.",
    },
    "OTROS": {
        "resumen_incidente": "El cliente reportó un ruido irregular al acelerar sin poder identificar el origen de la falla.",
        "diagnostico": "Ruido proveniente del tren delantero, compatible con desgaste de rótula o soporte de motor. Requiere revisión más detallada en taller.",
        "trabajo_realizado": "Se realizó una inspección visual y prueba de manejo. Se identificó el área del ruido y se aseguró que el vehículo puede circular con precaución.",
        "estado_final": "Vehículo operativo; la falla no compromete la seguridad inmediata pero debe atenderse.",
        "recomendaciones_preventivas": "Evitar caminos en mal estado hasta la revisión. Atender el ruido antes de que derive en una avería mayor.",
        "proximos_pasos": "Agendar una revisión del tren delantero y soportes de motor en taller.",
    },
}
JUSTIFICACION_ASIGNACION = {
    "BATERIA": "Asignado al técnico disponible más cercano (aprox. 2.1 km) con experiencia en sistemas eléctricos.",
    "LLANTA": "Asignado por proximidad (aprox. 1.4 km) y disponibilidad inmediata para cambio de neumático en sitio.",
    "MOTOR": "Asignado al técnico con especialidad en motores, a 3.0 km de la ubicación del incidente.",
    "CHOQUE": "Asignado al técnico más cercano (aprox. 2.7 km) para evaluación de daños tras la colisión.",
    "OTROS": "Asignado por cercanía y disponibilidad para diagnóstico general del vehículo.",
}
# Conversaciones precargadas: lista de (rol_emisor, contenido, relevante_tecnico).
CHAT_CLIENTE = {
    "BATERIA": [
        ("CLIENTE", "Hola, mi auto no arranca, creo que es la batería.", False),
        ("IA", "Hola. Por tu seguridad, asegurate de estar en un lugar alejado del tráfico. Contame: ¿las luces del tablero encienden aunque sea débilmente al girar la llave?", False),
        ("CLIENTE", "Sí, encienden pero muy débiles y solo hace un clic.", True),
        ("IA", "Eso confirma una batería muy descargada. No sigas girando la llave para no descargarla más. El técnico ya va en camino y lleva equipo de arranque asistido. Mantené el vehículo apagado mientras llega.", False),
    ],
    "LLANTA": [
        ("CLIENTE", "Se me pinchó una llanta en plena avenida.", False),
        ("IA", "Entendido. Prioridad tu seguridad: encendé las balizas, ubicá el vehículo lo más a la derecha posible y bajate por el lado de la vereda. ¿La llanta afectada es delantera o trasera?", False),
        ("CLIENTE", "Es la trasera derecha, quedó totalmente baja.", True),
        ("IA", "Perfecto, gracias. No manejes con la llanta desinflada para no dañar el aro. El técnico lleva lo necesario para el cambio y llega en breve.", False),
    ],
    "MOTOR": [
        ("CLIENTE", "Salió humo blanco del motor y perdió fuerza.", True),
        ("IA", "Es importante que apagues el motor de inmediato y no lo vuelvas a encender: el humo blanco suele indicar sobrecalentamiento. Alejate del vehículo unos metros y esperá. ¿Ves el testigo de temperatura encendido en el tablero?", False),
        ("CLIENTE", "Sí, está en rojo el de temperatura.", True),
        ("IA", "Confirmado sobrecalentamiento. No abras el radiador por ningún motivo, el vapor puede quemar. El técnico va en camino con refrigerante y herramientas.", False),
    ],
    "CHOQUE": [
        ("CLIENTE", "Tuve un choque de frente pero estoy bien.", False),
        ("IA", "Lo más importante es que estés bien. ¿Hay otras personas involucradas o heridos? Si es así, llamá también a emergencias médicas. Señalizá la zona con las balizas.", False),
        ("CLIENTE", "No, solo daño en el parachoques delantero.", True),
        ("IA", "Bien. Evitá mover mucho el vehículo hasta que llegue el técnico para evaluar si es seguro circular. Ya está en camino.", False),
    ],
    "OTROS": [
        ("CLIENTE", "El motor hace un ruido raro cuando acelero.", False),
        ("IA", "Gracias por avisar. Para cuidar el vehículo, evitá acelerar de forma brusca hasta la revisión. ¿El ruido aparece solo al acelerar o también en ralentí?", False),
        ("CLIENTE", "Solo cuando acelero, en frío casi no se escucha.", True),
        ("IA", "Anotado, ese detalle le sirve al técnico. Manejá con suavidad; el técnico llega para diagnosticar en sitio.", False),
    ],
}
CHAT_TECNICO = {
    "BATERIA": [
        ("IA", "Copiloto listo. Para este incidente de batería te sugiero llevar: cables de arranque o booster, multímetro, cepillo de bornes y una batería de reemplazo por si la carga no sostiene. El cliente confirmó que solo hace clic al arrancar.", False),
        ("TECNICO", "¿Conviene llevar batería nueva o pruebo primero con el booster?", False),
        ("IA", "Probá primero con el booster y medí la tensión de carga del alternador (debería dar ~14 V). Si la batería no sostiene sobre 12 V con el motor apagado, ofrecé el reemplazo.", False),
    ],
    "LLANTA": [
        ("IA", "Copiloto listo. Para el pinchazo llevá: gata hidráulica, llave de cruz, torquímetro y un kit de reparación por si el repuesto no está en condiciones. El cliente reporta la trasera derecha totalmente baja.", False),
        ("TECNICO", "¿Reviso las otras llantas también?", False),
        ("IA", "Sí, aprovechá para verificar la presión de las cuatro y el estado del repuesto antes de instalarlo. Ajustá el torque al valor del fabricante.", False),
    ],
    "MOTOR": [
        ("IA", "Copiloto listo. Incidente de sobrecalentamiento: llevá refrigerante, agua desmineralizada, guantes térmicos y sellante temporal de fugas. El cliente confirmó testigo de temperatura en rojo y humo blanco.", False),
        ("TECNICO", "¿Puedo dejarlo circular después de reponer refrigerante?", False),
        ("IA", "Solo de forma provisional y a baja exigencia. Recomendale traslado a taller para revisar junta de culata y hacer prueba de compresión; no debe forzar el motor.", False),
    ],
    "CHOQUE": [
        ("IA", "Copiloto listo. Para la colisión llevá: linterna, precintos/amarres, juego de destornilladores y cinta para asegurar piezas sueltas. Daño reportado en parachoques delantero, cliente sin heridas.", False),
        ("TECNICO", "¿Evalúo si puede circular por sus medios?", False),
        ("IA", "Sí. Verificá que no haya fugas, que las luces funcionen y que ninguna pieza roce la llanta. Si todo está firme, puede circular a baja velocidad hasta chapería.", False),
    ],
    "OTROS": [
        ("IA", "Copiloto listo. Ruido al acelerar: llevá elevador o gata, estetoscopio mecánico y juego de llaves. El cliente indica que el ruido aparece solo al acelerar y casi no se oye en frío.", False),
        ("TECNICO", "¿Por dónde empiezo el diagnóstico?", False),
        ("IA", "Empezá por el tren delantero y los soportes de motor con una prueba de manejo corta. El que aparezca solo al acelerar apunta a rótula o soporte con juego.", False),
    ],
}

# Plan de incidentes por tenant: (dias_atras, estado, clasificacion, prioridad,
# estado_pago). estado_pago None = sin pago.
PLAN_INCIDENTES = [
    (95, "ATENDIDO", "BATERIA", "MEDIA", "PAGADO"),
    (70, "ATENDIDO", "MOTOR", "ALTA", "PAGADO"),
    (45, "ATENDIDO", "LLANTA", "BAJA", "NO_PAGO"),
    (20, "CANCELADO", "CHOQUE", "ALTA", None),
    (8, "EN_PROCESO", "OTROS", "MEDIA", None),
    (4, "EN_CAMINO", "BATERIA", "MEDIA", None),
    (2, "ASIGNADO", "LLANTA", "BAJA", None),
    (1, "PENDIENTE", "MOTOR", "ALTA", None),
]

CADENA_ESTADOS = ["PENDIENTE", "EN_PROCESO_IA", "CLASIFICADO", "ASIGNADO", "EN_CAMINO", "EN_PROCESO", "ATENDIDO"]
NOTAS_HISTORIAL = {
    "PENDIENTE": "Incidente registrado por el cliente desde la aplicación móvil.",
    "EN_PROCESO_IA": "Procesando la descripción y evidencias con el sistema de IA.",
    "CLASIFICADO": "Clasificado automáticamente según la descripción del cliente.",
    "ASIGNADO": "Asignado al taller y técnico disponibles más cercanos.",
    "EN_CAMINO": "Técnico en camino hacia la ubicación del incidente.",
    "EN_PROCESO": "Técnico en sitio atendiendo el vehículo.",
    "ATENDIDO": "Incidente resuelto satisfactoriamente. Vehículo operativo.",
    "CANCELADO": "Cancelado por el cliente antes de recibir la atención.",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _punto(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)  # WKT: lng primero


def _make_session(db_url: str | None) -> Session:
    if db_url:
        return sessionmaker(bind=create_engine(db_url))()
    from app.core.database import SessionLocal
    return SessionLocal()


class _Nombres:
    """Reparte nombres de pila únicos globalmente, evitando correos ya usados."""

    def __init__(self, correos_existentes: set[str]):
        self._pool = iter(NOMBRES_PILA)
        self._existentes = correos_existentes

    def siguiente(self, rol_dominio: str) -> tuple[str, str]:
        for nombre in self._pool:
            correo = f"{nombre}@{rol_dominio}.com"
            if correo not in self._existentes:
                self._existentes.add(correo)
                return nombre, correo
        raise RuntimeError("Se agotó el pool de nombres de pila para el seed.")


def _crear_usuario(db, correo, nombre_completo, rol, tid, hash_pw, tel_prefix, i):
    u = USUARIOS(
        CORREO_ELECTRONICO=correo,
        HASH_CONTRASENA=hash_pw,
        NOMBRE_COMPLETO=nombre_completo,
        TELEFONO=f"{tel_prefix}{7000000 + i}",
        ROL=rol,
        ACTIVO=True,
        ID_TENANT=tid,
    )
    db.add(u)
    db.flush()
    return u


def seed_tenant(db: Session, tenant: Tenant, idx: int, nombres: _Nombres, hash_pw: str) -> None:
    tid = tenant.ID_TENANT
    print(f"\n  [{idx + 1}] {tenant.NOMBRE} (id_tenant={tid})")

    if db.query(USUARIOS).filter(USUARIOS.ID_TENANT == tid).first():
        print("      >> Ya tiene usuarios, se saltea.")
        return

    lat_ws, lng_ws = BASE_COORDS[idx % len(BASE_COORDS)]

    # ── Taller ────────────────────────────────────────────────────────────────
    nom_taller, correo_taller = nombres.siguiente("taller")
    ap = APELLIDOS[idx % len(APELLIDOS)]
    ws_user = _crear_usuario(
        db, correo_taller, f"{nom_taller.capitalize()} {ap}", "TALLER", tid, hash_pw, "70", idx
    )
    taller = TALLERES(
        ID_USUARIO=ws_user.ID_USUARIO,
        NOMBRE_NEGOCIO=NOMBRES_NEGOCIO[idx % len(NOMBRES_NEGOCIO)],
        NIT=f"{1000000 + idx * 13371:07d}-1",
        DIRECCION=DIRECCIONES[idx % len(DIRECCIONES)],
        TASA_COMISION=Decimal("10.00"),
        LATITUD=Decimal(str(round(lat_ws, 7))),
        LONGITUD=Decimal(str(round(lng_ws, 7))),
        ACTIVO=True,
        ID_TENANT=tid,
    )
    db.add(taller)
    db.flush()

    # ── Técnicos ────────────────────────────────────────────────────────────────
    tecnicos = []
    for ti in range(2):
        nom_tec, correo_tec = nombres.siguiente("tecnico")
        tu = _crear_usuario(
            db, correo_tec, f"{nom_tec.capitalize()} {APELLIDOS[(idx + ti + 1) % len(APELLIDOS)]}",
            "TECNICO", tid, hash_pw, "71", idx * 10 + ti,
        )
        tec = TECNICOS(
            ID_TALLER=taller.ID_TALLER,
            ID_USUARIO=tu.ID_USUARIO,
            NOMBRE_COMPLETO=tu.NOMBRE_COMPLETO,
            TELEFONO=tu.TELEFONO,
            DISPONIBLE=True,
            UBICACION_ACTUAL=_punto(lat_ws + 0.003 * (ti + 1), lng_ws - 0.002 * (ti + 1)),
        )
        db.add(tec)
        db.flush()
        tecnicos.append(tec)

    # ── Clientes + vehículos ─────────────────────────────────────────────────────
    clientes, vehiculos = [], []
    for ci in range(3):
        nom_cli, correo_cli = nombres.siguiente("cliente")
        cu = _crear_usuario(
            db, correo_cli, f"{nom_cli.capitalize()} {APELLIDOS[(idx + ci + 4) % len(APELLIDOS)]}",
            "CLIENTE", tid, hash_pw, "60", idx * 10 + ci,
        )
        db.add(CLIENTES(ID_USUARIO=cu.ID_USUARIO))
        db.flush()
        clientes.append(cu)

        marca, modelo, anio = VEHICULOS_DATA[(idx * 3 + ci) % len(VEHICULOS_DATA)]
        veh = VEHICULOS(
            ID_USUARIO_CLIENTE=cu.ID_USUARIO,
            MARCA=marca,
            MODELO=modelo,
            ANIO=anio,
            PLACA=f"{2000 + idx * 100 + ci}-{chr(65 + idx)}{chr(66 + ci)}{chr(70 + idx)}",
        )
        db.add(veh)
        db.flush()
        vehiculos.append(veh)

    # ── Incidentes ────────────────────────────────────────────────────────────────
    for i, (dias, estado, clasif, prior, pago_estado) in enumerate(PLAN_INCIDENTES):
        cliente = clientes[i % len(clientes)]
        vehiculo = vehiculos[i % len(vehiculos)]
        tecnico = tecnicos[i % len(tecnicos)]
        creado = _utcnow() - timedelta(days=dias)
        lat_i = lat_ws + (0.01 if i % 2 else -0.012) * ((i % 3) + 1) * 0.4
        lng_i = lng_ws + (-0.011 if i % 2 else 0.009) * ((i % 3) + 1) * 0.4

        inc = INCIDENTES(
            ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
            ID_VEHICULO=vehiculo.ID_VEHICULO,
            UBICACION=_punto(lat_i, lng_i),
            ESTADO=estado,
            PRIORIDAD=prior,
            CLASIFICACION=clasif,
            RESUMEN_IA=RESUMEN_IA[clasif],
            TIEMPO_ESTIMADO_LLEGADA_MINUTOS=15 + (i * 5) % 30,
            ID_TENANT=tid,
            FECHA_CREACION=creado,
        )
        db.add(inc)
        db.flush()

        # Historial coherente con el estado final.
        if estado == "CANCELADO":
            estados = ["PENDIENTE", "CANCELADO"]
        else:
            estados = CADENA_ESTADOS[: CADENA_ESTADOS.index(estado) + 1]
        t = creado
        for st in estados:
            t += timedelta(minutes=12)
            nota = NOTAS_HISTORIAL[st]
            if st == "ASIGNADO":
                nota = f"{nota} {JUSTIFICACION_ASIGNACION[clasif]}"
            db.add(HISTORIAL_INCIDENTES(
                ID_INCIDENTE=inc.ID_INCIDENTE, ESTADO=st, NOTAS=nota,
                ID_USUARIO_CAMBIO=ws_user.ID_USUARIO, FECHA_CAMBIO=t,
            ))
        db.flush()

        tiene_asignacion = estado in ("ASIGNADO", "EN_CAMINO", "EN_PROCESO", "ATENDIDO")
        if not tiene_asignacion:
            continue

        monto, comision = payment_service.calcular_tarifa(clasif, prior)
        con_cotizacion = estado in ("EN_CAMINO", "EN_PROCESO", "ATENDIDO")
        asig = ASIGNACIONES(
            ID_INCIDENTE=inc.ID_INCIDENTE,
            ID_TALLER=taller.ID_TALLER,
            ID_TECNICO=tecnico.ID_TECNICO,
            FECHA_ASIGNACION=creado + timedelta(minutes=20),
            FECHA_ACEPTACION=(creado + timedelta(minutes=28)) if estado != "ASIGNADO" else None,
            MONTO_COTIZADO=monto if con_cotizacion else None,
            TIEMPO_ESTIMADO_REPARACION=(45 + i * 10) if con_cotizacion else None,
            COTIZACION_ACEPTADA=True if con_cotizacion else None,
            NOTAS_COTIZACION="Cotización aceptada por el cliente." if con_cotizacion else None,
        )
        db.add(asig)
        db.flush()

        # Técnico ocupado si el servicio está en curso.
        if estado in ("EN_CAMINO", "EN_PROCESO"):
            tecnico.DISPONIBLE = False
            db.add(tecnico)

        # Chats de atención (cliente + copiloto técnico) para servicios activos/cerrados.
        if estado in ("EN_PROCESO", "ATENDIDO"):
            conv_cli = CONVERSACIONES(ID_INCIDENTE=inc.ID_INCIDENTE, TIPO="CLIENTE", ID_TENANT=tid)
            db.add(conv_cli)
            db.flush()
            for rol, contenido, relevante in CHAT_CLIENTE[clasif]:
                db.add(MENSAJES_CHAT(
                    ID_CONVERSACION=conv_cli.ID_CONVERSACION,
                    ROL_EMISOR=rol,
                    ID_USUARIO_EMISOR=cliente.ID_USUARIO if rol == "CLIENTE" else None,
                    CONTENIDO=contenido,
                    RELEVANTE_TECNICO=relevante,
                ))
            conv_tec = CONVERSACIONES(ID_INCIDENTE=inc.ID_INCIDENTE, TIPO="TECNICO", ID_TENANT=tid)
            db.add(conv_tec)
            db.flush()
            for rol, contenido, _ in CHAT_TECNICO[clasif]:
                db.add(MENSAJES_CHAT(
                    ID_CONVERSACION=conv_tec.ID_CONVERSACION,
                    ROL_EMISOR=rol,
                    ID_USUARIO_EMISOR=tecnico.ID_USUARIO if rol == "TECNICO" else None,
                    CONTENIDO=contenido,
                ))
            db.flush()

        if estado != "ATENDIDO":
            continue

        # ── Evidencias (con campos de IA a mano) ────────────────────────────────
        db.add(EVIDENCIAS(
            ID_INCIDENTE=inc.ID_INCIDENTE, TIPO="IMAGEN",
            URL_ARCHIVO=f"/static/evidencias/{inc.ID_INCIDENTE}/foto.jpg",
            CLAVE_ARCHIVO=f"evidencias/{inc.ID_INCIDENTE}/foto.jpg",
            ANALISIS_IA=EVIDENCIA_IMAGEN_ANALISIS[clasif],
        ))
        db.add(EVIDENCIAS(
            ID_INCIDENTE=inc.ID_INCIDENTE, TIPO="AUDIO",
            URL_ARCHIVO=f"/static/evidencias/{inc.ID_INCIDENTE}/audio.m4a",
            CLAVE_ARCHIVO=f"evidencias/{inc.ID_INCIDENTE}/audio.m4a",
            TEXTO_TRANSCRITO=EVIDENCIA_AUDIO_TRANSCRIPCION[clasif],
        ))
        db.flush()

        # ── Pago ────────────────────────────────────────────────────────────────
        pagado = creado + timedelta(days=1)
        db.add(PAGOS(
            ID_INCIDENTE=inc.ID_INCIDENTE,
            ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
            ID_TALLER=taller.ID_TALLER,
            ID_ASIGNACION=asig.ID_ASIGNACION,
            MONTO=monto,
            COMISION_PLATAFORMA=comision,
            ESTADO=pago_estado,
            METODO_PAGO="TRANSFERENCIA" if i % 2 else "EFECTIVO",
            FECHA_CREACION=pagado,
            FECHA_MARCADO_PAGO=pagado if pago_estado == "PAGADO" else None,
            FECHA_CONFIRMACION=(pagado + timedelta(hours=6)) if pago_estado == "PAGADO" else None,
            ID_TENANT=tid,
        ))
        db.flush()

        # ── Informe de servicio (contenido de IA a mano) ────────────────────────
        db.add(INFORMES_SERVICIO(
            ID_INCIDENTE=inc.ID_INCIDENTE,
            ID_TENANT=tid,
            ESTADO="LISTO",
            CONTENIDO_IA=INFORME_CONTENIDO[clasif],
            URL_ARCHIVO=f"/static/informes/{inc.ID_INCIDENTE}/informe.pdf",
            CLAVE_ARCHIVO=f"informes/{inc.ID_INCIDENTE}/informe.pdf",
            GENERADO_POR_IA=True,
            CORREO_ENVIADO=True,
            FECHA_GENERACION=creado + timedelta(hours=2),
        ))
        db.flush()

    db.commit()
    print(f"      OK  taller:1  tecnicos:{len(tecnicos)}  clientes:{len(clientes)}  "
          f"vehiculos:{len(vehiculos)}  incidentes:{len(PLAN_INCIDENTES)}")


def main() -> None:
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    db = _make_session(db_url)
    try:
        correos = {c for (c,) in db.query(USUARIOS.CORREO_ELECTRONICO).all()}
        nombres = _Nombres(correos)
        hash_pw = hashear_contrasena(PASSWORD)  # un hash bcrypt válido de "12345678"

        for idx, nombre in enumerate(TENANTS):
            tenant = db.query(Tenant).filter(Tenant.NOMBRE == nombre).first()
            if tenant is None:
                tenant = Tenant(NOMBRE=nombre, DESCRIPCION=f"Red de talleres — {nombre}", ACTIVO=True)
                db.add(tenant)
                db.commit()
                db.refresh(tenant)
                print(f"Tenant creado: {nombre} (id={tenant.ID_TENANT})")
            try:
                seed_tenant(db, tenant, idx, nombres, hash_pw)
            except Exception as exc:
                db.rollback()
                print(f"      ERROR sembrando {nombre}: {exc}")
                raise
        print("\nSeed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
