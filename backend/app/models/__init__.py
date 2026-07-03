"""Importar este paquete registra todos los modelos en Base.metadata."""

import app.modules.incidents.models  # noqa: F401
import app.modules.bitacora.models  # noqa: F401
import app.modules.tenants.models  # noqa: F401
import app.modules.users.models  # noqa: F401
import app.modules.vehicles.models  # noqa: F401
import app.modules.workshops.models  # noqa: F401
import app.modules.technicians.models  # noqa: F401
import app.modules.payments.models  # noqa: F401
import app.modules.assignments.models  # noqa: F401
