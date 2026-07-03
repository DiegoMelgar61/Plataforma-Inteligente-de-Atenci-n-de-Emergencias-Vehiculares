"""Importar este paquete registra todos los modelos en Base.metadata."""

import app.models.models  # noqa: F401
import app.modules.bitacora.models  # noqa: F401
import app.modules.tenants.models  # noqa: F401
import app.modules.users.models  # noqa: F401
