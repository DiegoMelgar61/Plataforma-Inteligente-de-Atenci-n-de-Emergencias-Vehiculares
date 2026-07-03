#!/usr/bin/env python3
"""
Populate non-principal tenants with realistic seed data.

Usage (run from backend/ directory):
    python scripts/seed_tenants.py

Creates per tenant (skips already-seeded tenants):
    - 1 workshop user + workshop record
    - 2 technicians (with user accounts)
    - 3 client users + 1 vehicle each
    - 8 incidents spread over 6 months with varied states
    - Assignments, state history, and payments for completed incidents

All passwords follow the pattern:  Taller1234! / Tecnico1234! / Cliente1234!
"""

import sys
import uuid
import bcrypt
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2.elements import WKTElement


def _make_session(db_url: str | None) -> Session:
    if db_url:
        engine = create_engine(db_url)
    else:
        from app.core.database import SessionLocal
        return SessionLocal()
    return sessionmaker(bind=engine)()
from app.modules.assignments.models import ASIGNACIONES
from app.modules.incidents.models import HISTORIAL_INCIDENTES, INCIDENTES
from app.modules.payments.models import PAGOS
from app.modules.technicians.models import TECNICOS
from app.modules.tenants.models import Tenant
from app.modules.users.models import CLIENTES, USUARIOS
from app.modules.vehicles.models import VEHICULOS
from app.modules.workshops.models import TALLERES

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

TENANT_DEFAULT_ID = uuid.UUID("e76212eb-e845-411d-b37f-e0ec986564d8")

# ──────────────────────────────────────────────────────────────
# Data pools  (Santa Cruz de la Sierra, Bolivia flavour)
# ──────────────────────────────────────────────────────────────

FIRST_NAMES_M = [
    "Rodrigo", "Mauricio", "Gustavo", "Pablo", "Javier",
    "Marco", "Ernesto", "Rubén", "Nelson", "Cristian",
    "Álvaro", "Sebastián", "Gonzalo", "Hugo", "Raúl",
]
FIRST_NAMES_F = [
    "Alejandra", "Verónica", "Claudia", "Natalia", "Gabriela",
    "Isabel", "Rosa", "Carmen", "Teresa", "Patricia",
    "Jimena", "Cecilia", "Lorena", "Beatriz", "Daniela",
]
LAST_NAMES = [
    "Andrade Bustamante", "Sandoval Pereira", "Herrera Montaño",
    "Quispe Torrez", "Mamani Flores", "Salinas Vaca",
    "Suárez Roca", "Melgar Paz", "Chávez Ortiz", "Vargas Soliz",
    "Montaño Cruz", "Pedraza Aguilar", "Torrico Méndez",
    "Vaca Cuellar", "Arce Ibáñez", "Balcázar Rueda",
    "Peñaranda Daza", "Mercado Ribera", "Cabrera Loza", "Antelo Gutiérrez",
]

WORKSHOP_NAMES = [
    "Taller Mecánico Don Pepe",
    "AutoService San Martín",
    "Mecánica El Progreso",
    "Taller Automotriz Banzer",
    "AutoCenter Los Pozos",
    "Mecánica Integral Quispe",
    "Servicio Técnico Conavi",
    "Taller El Rápido",
    "Automotriz Santa Cruz",
    "Centro Mecánico Equipetrol",
]

DIRECCIONES = [
    "Av. Banzer km 6, Zona Norte",
    "Calle Sucre #245, Plan 3000",
    "Av. Cristo Redentor #890, Zona Sur",
    "Radial 27 #156, Zona Este",
    "Av. Paragua #578, Villa 1ro de Mayo",
    "Calle Murillo #34, Barrio Hamacas",
    "Av. Roca y Coronado #120, Zona Oeste",
    "Calle Independencia #67, Barrio Recoleta",
    "Av. Busch #312, Plan 2000",
    "Calle Bolivia #89, Barrio El Trompillo",
]

VEHICLE_DATA = [
    ("Toyota",      "Corolla",   2019),
    ("Chevrolet",   "Sail",      2020),
    ("Nissan",      "Tiida",     2018),
    ("Hyundai",     "Accent",    2021),
    ("Toyota",      "RAV4",      2020),
    ("Suzuki",      "Swift",     2017),
    ("Kia",         "Sportage",  2022),
    ("Volkswagen",  "Gol",       2018),
    ("Ford",        "EcoSport",  2019),
    ("Chevrolet",   "Cruze",     2021),
    ("Mitsubishi",  "L200",      2019),
    ("Toyota",      "Hilux",     2020),
]

RESUMENES_IA = {
    "BATERIA": "Vehículo sin arranque por descarga total de batería. Se recomienda revisión del sistema eléctrico y diagnóstico del alternador.",
    "LLANTA":  "Pinchazo en neumático trasero derecho. Requiere cambio de llanta en sitio o traslado a taller cercano.",
    "CHOQUE":  "Colisión frontal leve con daños en parachoques y cofre. Evaluación estructural necesaria antes de continuar circulando.",
    "MOTOR":   "Falla crítica en motor: pérdida de potencia con humo blanco. Posible ruptura de junta de culata o problema en sistema de refrigeración.",
    "OTROS":   "Falla mecánica no identificada. El vehículo presenta comportamiento irregular. Diagnóstico completo requerido en taller.",
}

NOTAS_HISTORIAL = {
    "PENDIENTE":     "Incidente registrado por el cliente desde la aplicación móvil.",
    "EN_PROCESO_IA": "Procesando descripción con IA para clasificación automática.",
    "CLASIFICADO":   "Clasificado automáticamente por el sistema de inteligencia artificial.",
    "ASIGNADO":      "Asignado al taller disponible más cercano según geolocalización.",
    "EN_CAMINO":     "Técnico en camino hacia la ubicación del incidente.",
    "EN_PROCESO":    "Técnico presente en sitio, atendiendo el vehículo.",
    "ATENDIDO":      "Incidente resuelto satisfactoriamente. Vehículo operativo.",
    "CANCELADO":     "Cancelado por el cliente antes de recibir atención.",
}

# Santa Cruz de la Sierra base coordinates  (lat, lng)
BASE_COORDS = [
    (-17.7840, -63.1812),
    (-17.7950, -63.1650),
    (-17.7720, -63.2010),
    (-17.8100, -63.1750),
    (-17.7660, -63.1920),
    (-17.8200, -63.1600),
    (-17.7800, -63.2100),
    (-17.7500, -63.1800),
    (-17.8050, -63.1500),
    (-17.7600, -63.2050),
]

# 8 incidents per tenant: (months_ago, final_state, clasificacion, prioridad, has_assignment, payment_state)
INCIDENT_PLAN = [
    (6, "ATENDIDO",   "BATERIA", "MEDIA", True,  "PAGADO"),
    (5, "ATENDIDO",   "LLANTA",  "BAJA",  True,  "PAGADO"),
    (4, "ATENDIDO",   "MOTOR",   "ALTA",  True,  "PAGADO"),
    (3, "CANCELADO",  "CHOQUE",  "ALTA",  False, None),
    (2, "ATENDIDO",   "BATERIA", "MEDIA", True,  "NO_PAGO"),
    (1, "EN_PROCESO", "LLANTA",  "BAJA",  True,  None),
    (0, "ASIGNADO",   "OTROS",   "MEDIA", True,  None),   # 2 weeks ago
    (0, "PENDIENTE",  "MOTOR",   "ALTA",  False, None),  # 5 days ago
]

STATE_CHAIN = ["PENDIENTE", "EN_PROCESO_IA", "CLASIFICADO", "ASIGNADO", "EN_CAMINO", "EN_PROCESO", "ATENDIDO"]

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _months_ago(n: int, rng: random.Random, jitter: int = 4) -> datetime:
    base = _utcnow() - timedelta(days=n * 30)
    return base - timedelta(days=rng.randint(0, jitter), hours=rng.randint(0, 23))


def _point(lat: float, lng: float) -> WKTElement:
    # WKT order: longitude first, then latitude
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def _slug(name: str) -> str:
    replacements = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", " ": "."}
    return "".join(replacements.get(c.lower(), c.lower()) for c in name)


def _email(name: str, tenant_idx: int, role: str, n: int = 0) -> str:
    return f"{_slug(name)}.t{tenant_idx}.{role}{n}@seed.dev"


def _plate(tenant_idx: int, n: int) -> str:
    """Unique plate per (tenant, vehicle_index)."""
    letters = "ABCDEFGHJKLMNPRSTUVWXYZ"
    num  = (tenant_idx * 100 + n + 1000) % 9000 + 1000
    suf  = "".join(letters[(tenant_idx * p + n + i) % len(letters)] for i, p in enumerate([3, 7, 11]))
    return f"{num}-{suf}"


def _nit(tenant_idx: int) -> str:
    return f"{1000000 + tenant_idx * 13371:07d}-1"


def _monto(clasif: str, rng: random.Random) -> Decimal:
    ranges = {
        "BATERIA": (150, 500),
        "LLANTA":  (80,  250),
        "CHOQUE":  (800, 3000),
        "MOTOR":   (500, 2000),
        "OTROS":   (200, 800),
    }
    lo, hi = ranges.get(clasif, (200, 800))
    return Decimal(str(rng.randint(lo // 10, hi // 10) * 10))


# ──────────────────────────────────────────────────────────────
# Core seeding logic
# ──────────────────────────────────────────────────────────────

def _add_historial(
    db: Session,
    inc: INCIDENTES,
    final_state: str,
    created_at: datetime,
    changed_by_id: uuid.UUID,
    rng: random.Random,
) -> None:
    if final_state == "CANCELADO":
        states = ["PENDIENTE", "CANCELADO"]
    elif final_state in STATE_CHAIN:
        idx = STATE_CHAIN.index(final_state)
        states = STATE_CHAIN[: idx + 1]
    else:
        states = ["PENDIENTE"]

    t = created_at
    for state in states:
        t += timedelta(minutes=rng.randint(5, 25))
        db.add(HISTORIAL_INCIDENTES(
            ID_HISTORIAL=uuid.uuid4(),
            ID_INCIDENTE=inc.ID_INCIDENTE,
            ESTADO=state,
            NOTAS=NOTAS_HISTORIAL.get(state, ""),
            ID_USUARIO_CAMBIO=changed_by_id,
            FECHA_CAMBIO=t,
        ))
    db.flush()


def seed_tenant(db: Session, tenant: Tenant, tenant_idx: int) -> None:
    tid = tenant.ID_TENANT
    print(f"\n  [{tenant_idx + 1}] {tenant.NOMBRE} ({str(tid)[:8]}...)")

    existing = db.query(INCIDENTES).filter(INCIDENTES.ID_TENANT == tid).first()
    if existing:
        print("      >> Already seeded, skipping.")
        return

    rng = random.Random(str(tid))  # deterministic per tenant
    lat_ws, lng_ws = BASE_COORDS[tenant_idx % len(BASE_COORDS)]

    # ── Workshop user ──────────────────────────────────────────
    ws_fn   = rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)
    ws_ln   = rng.choice(LAST_NAMES)
    ws_full = f"{ws_fn} {ws_ln}"

    ws_user = USUARIOS(
        ID_USUARIO=uuid.uuid4(),
        CORREO_ELECTRONICO=_email(ws_full, tenant_idx, "taller"),
        HASH_CONTRASENA=_hash("Taller1234!"),
        NOMBRE_COMPLETO=ws_full,
        TELEFONO=f"7{rng.randint(1000000, 9999999)}",
        ROL="TALLER",
        ACTIVO=True,
        ID_TENANT=tid,
        FECHA_CREACION=_months_ago(7, rng),
    )
    db.add(ws_user)
    db.flush()

    taller = TALLERES(
        ID_TALLER=uuid.uuid4(),
        ID_USUARIO=ws_user.ID_USUARIO,
        NOMBRE_NEGOCIO=WORKSHOP_NAMES[tenant_idx % len(WORKSHOP_NAMES)],
        NIT=_nit(tenant_idx),
        DIRECCION=DIRECCIONES[tenant_idx % len(DIRECCIONES)],
        TASA_COMISION=Decimal("10.00"),
        LATITUD=Decimal(str(round(lat_ws, 7))),
        LONGITUD=Decimal(str(round(lng_ws, 7))),
        ACTIVO=True,
        ID_TENANT=tid,
        FECHA_CREACION=_months_ago(7, rng),
    )
    db.add(taller)
    db.flush()

    # ── Technicians ────────────────────────────────────────────
    tecnicos = []
    for ti in range(2):
        fn   = rng.choice(FIRST_NAMES_M)
        ln   = rng.choice(LAST_NAMES)
        full = f"{fn} {ln}"
        tu   = USUARIOS(
            ID_USUARIO=uuid.uuid4(),
            CORREO_ELECTRONICO=_email(full, tenant_idx, "tecnico", ti),
            HASH_CONTRASENA=_hash("Tecnico1234!"),
            NOMBRE_COMPLETO=full,
            TELEFONO=f"7{rng.randint(1000000, 9999999)}",
            ROL="TECNICO",
            ACTIVO=True,
            ID_TENANT=tid,
            FECHA_CREACION=_months_ago(6, rng),
        )
        db.add(tu)
        db.flush()

        tec = TECNICOS(
            ID_TECNICO=uuid.uuid4(),
            ID_TALLER=taller.ID_TALLER,
            ID_USUARIO=tu.ID_USUARIO,
            NOMBRE_COMPLETO=full,
            TELEFONO=tu.TELEFONO,
            DISPONIBLE=True,
            UBICACION_ACTUAL=_point(
                lat_ws + rng.uniform(-0.005, 0.005),
                lng_ws + rng.uniform(-0.005, 0.005),
            ),
            FECHA_CREACION=_months_ago(6, rng),
        )
        db.add(tec)
        db.flush()
        tecnicos.append(tec)

    # ── Clients + vehicles ─────────────────────────────────────
    clientes  = []
    vehiculos = []
    for ci in range(3):
        fn   = rng.choice(FIRST_NAMES_M + FIRST_NAMES_F)
        ln   = rng.choice(LAST_NAMES)
        full = f"{fn} {ln}"
        cu   = USUARIOS(
            ID_USUARIO=uuid.uuid4(),
            CORREO_ELECTRONICO=_email(full, tenant_idx, "cliente", ci),
            HASH_CONTRASENA=_hash("Cliente1234!"),
            NOMBRE_COMPLETO=full,
            TELEFONO=f"6{rng.randint(1000000, 9999999)}",
            ROL="CLIENTE",
            ACTIVO=True,
            ID_TENANT=tid,
            FECHA_CREACION=_months_ago(5, rng),
        )
        db.add(cu)
        db.flush()
        db.add(CLIENTES(ID_USUARIO=cu.ID_USUARIO))
        db.flush()
        clientes.append(cu)

        marca, modelo, anio = rng.choice(VEHICLE_DATA)
        veh = VEHICULOS(
            ID_VEHICULO=uuid.uuid4(),
            ID_USUARIO_CLIENTE=cu.ID_USUARIO,
            MARCA=marca,
            MODELO=modelo,
            ANIO=anio,
            PLACA=_plate(tenant_idx, ci),
            FECHA_CREACION=_months_ago(5, rng),
        )
        db.add(veh)
        db.flush()
        vehiculos.append(veh)

    # ── 8 incidents ────────────────────────────────────────────
    for idx, (months, estado, clasif, prior, has_assign, pay_state) in enumerate(INCIDENT_PLAN):
        client  = clientes[idx % len(clientes)]
        vehicle = vehiculos[idx % len(vehiculos)]
        tecnico = tecnicos[idx % len(tecnicos)]

        if months == 0:
            created_at = _utcnow() - timedelta(days=(14 if idx == 6 else 5))
        else:
            created_at = _months_ago(months, rng)

        lat_i = lat_ws + rng.uniform(-0.025, 0.025)
        lng_i = lng_ws + rng.uniform(-0.025, 0.025)

        inc = INCIDENTES(
            ID_INCIDENTE=uuid.uuid4(),
            ID_USUARIO_CLIENTE=client.ID_USUARIO,
            ID_VEHICULO=vehicle.ID_VEHICULO,
            UBICACION=_point(lat_i, lng_i),
            ESTADO=estado,
            PRIORIDAD=prior,
            CLASIFICACION=clasif,
            RESUMEN_IA=RESUMENES_IA[clasif],
            TIEMPO_ESTIMADO_LLEGADA_MINUTOS=rng.randint(10, 45),
            ID_TENANT=tid,
            FECHA_CREACION=created_at,
        )
        db.add(inc)
        db.flush()

        _add_historial(db, inc, estado, created_at, ws_user.ID_USUARIO, rng)

        if not has_assign:
            continue

        monto    = _monto(clasif, rng)
        comision = (monto * Decimal("10") / Decimal("100")).quantize(Decimal("0.01"))
        assign_at = created_at + timedelta(minutes=rng.randint(10, 35))

        needs_cotizacion = estado in ("ATENDIDO", "EN_PROCESO")
        asig = ASIGNACIONES(
            ID_ASIGNACION=uuid.uuid4(),
            ID_INCIDENTE=inc.ID_INCIDENTE,
            ID_TALLER=taller.ID_TALLER,
            ID_TECNICO=tecnico.ID_TECNICO,
            FECHA_ASIGNACION=assign_at,
            FECHA_ACEPTACION=assign_at + timedelta(minutes=rng.randint(3, 15)) if estado != "ASIGNADO" else None,
            MONTO_COTIZADO=monto if needs_cotizacion else None,
            TIEMPO_ESTIMADO_REPARACION=rng.randint(30, 240) if needs_cotizacion else None,
            COTIZACION_ACEPTADA=True if needs_cotizacion else None,
            NOTAS_COTIZACION="Cotización aprobada por el cliente." if needs_cotizacion else None,
        )
        db.add(asig)
        db.flush()

        if pay_state:
            paid_at = created_at + timedelta(days=rng.randint(1, 3), hours=rng.randint(1, 8))
            confirmed_at = paid_at + timedelta(hours=rng.randint(1, 12)) if pay_state == "PAGADO" else None
            db.add(PAGOS(
                ID_PAGO=uuid.uuid4(),
                ID_INCIDENTE=inc.ID_INCIDENTE,
                ID_USUARIO_CLIENTE=client.ID_USUARIO,
                ID_TALLER=taller.ID_TALLER,
                ID_ASIGNACION=asig.ID_ASIGNACION,
                MONTO=monto,
                COMISION_PLATAFORMA=comision,
                ESTADO=pay_state,
                METODO_PAGO="TRANSFERENCIA" if rng.random() > 0.4 else "EFECTIVO",
                FECHA_CREACION=paid_at,
                FECHA_MARCADO_PAGO=paid_at if pay_state == "PAGADO" else None,
                FECHA_CONFIRMACION=confirmed_at,
                ID_TENANT=tid,
            ))
            db.flush()

    db.commit()

    talleres_count  = 1
    tecnicos_count  = 2
    clientes_count  = 3
    vehiculos_count = 3
    inc_count       = len(INCIDENT_PLAN)
    print(f"      OK taller: {talleres_count}  tecnicos: {tecnicos_count}  clientes: {clientes_count}  "
          f"vehiculos: {vehiculos_count}  incidentes: {inc_count}")


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

def main() -> None:
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    db: Session = _make_session(db_url)
    try:
        tenants = (
            db.query(Tenant)
            .filter(Tenant.ID_TENANT != TENANT_DEFAULT_ID, Tenant.ACTIVO.is_(True))
            .order_by(Tenant.FECHA_CREACION)
            .all()
        )

        if not tenants:
            print("No non-principal active tenants found. Nothing to seed.")
            return

        print(f"Found {len(tenants)} tenant(s) to process.\n")

        for i, tenant in enumerate(tenants):
            try:
                seed_tenant(db, tenant, i)
            except Exception as exc:
                db.rollback()
                print(f"      ERROR seeding {tenant.NOMBRE}: {exc}")
                raise

        print("\nAll done.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
