---
titulo: "Workflow de Desarrollo"
tipo: Desarrollo
fecha: 2026-07-05
tags: [workflow, git, dev, main, pr]
---

# Workflow de Desarrollo

Todo cambio nuevo se implementa en `dev`. `main` representa producción y solo recibe cambios mediante Pull Request desde `dev`.

## Flujo Principal

1. Trabajar en `dev`.
2. Implementar la funcionalidad o corrección.
3. Verificar localmente lo que corresponda: backend, frontend, mobile o documentación.
4. Commit con mensaje convencional.
5. Push a `origin/dev`.
6. Abrir PR `dev` → `main`.
7. Validar producción después del merge.

## Reglas

| Regla | Motivo |
|-------|--------|
| No trabajar directo en `main` | Evita romper producción |
| Mantener commits por unidad de trabajo | Facilita review y rollback |
| Documentar decisiones en `docs/` | Mantiene trazabilidad |
| Versionar `docs/` | El contexto viaja con el código |
| Ignorar `.vscode/` | Configuración local del editor |
| Ignorar `docs/.obsidian/workspace.json` | Estado visual local de Obsidian |

## Verificación Recomendada

| Capa | Comando |
|------|---------|
| Backend | `python -m compileall app` |
| Backend tests | `pytest` |
| Frontend | `npm run build` |
| Mobile | `flutter analyze` |

## Cuando Crear PR

Crear PR cuando se cumpla esto:

- La funcionalidad está completa para el alcance acordado.
- No quedan cambios accidentales en archivos no relacionados.
- La documentación relevante está actualizada.
- La verificación mínima de la capa tocada fue ejecutada o queda documentado por qué no se pudo ejecutar.

## Documentos Relacionados

- [[Estado Actual del Proyecto]]
- [[Conventions]]
- [[Testing]]
- [[Roadmap y TODOs]]
