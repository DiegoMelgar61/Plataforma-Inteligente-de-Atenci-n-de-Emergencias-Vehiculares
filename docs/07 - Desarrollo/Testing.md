---
titulo: "Testing"
tipo: Desarrollo
fecha: 2026-07-03
tags: [testing, pytest, jest, flutter_test]
---

# Testing

## Backend (pytest)

```bash
cd backend

# Ejecutar todos los tests
pytest

# Ejecutar con verbose
pytest -v

# Ejecutar tests específicos
pytest tests/test_technician_flow.py -v

# Ejecutar con cobertura
pytest --cov=app tests/
```

### Tests Existentes

- `test_app_smoke.py`: Tests de smoke (endpoints básicos)
- `test_technician_flow.py`: Flujo completo de técnico

### Estado Actual

⚠️ Los tests fallan contra Supabase (entorno de producción). Necesitan una DB local de test.

### Estrategia

- Tests unitarios por módulo
- Tests de integración con TestClient de FastAPI
- SQLite en memoria para tests rápidos
- PostGIS mocked con Text en tests

## Frontend (Karma/Jest)

```bash
cd frontend

# Ejecutar tests
ng test

# Ejecutar con cobertura
ng test --code-coverage
```

## Mobile (flutter_test)

```bash
cd mobile

# Ejecutar tests
flutter test

# Ejecutar con cobertura
flutter test --coverage
```

## Documentos Relacionados

- [[Setup Local]]
- [[Backend]]
- [[Resumen del Proyecto]]
