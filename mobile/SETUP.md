# Setup de Emergencias Vehiculares - Mobile

## ✅ Estructura completada

```
mobile/
├── lib/
│   ├── core/              # Config, API Client, Constants
│   ├── data/              # Models, Repositories
│   ├── presentation/      # UI, Providers, Routes
│   ├── shared/            # Widgets reutilizables
│   └── main.dart          # Punto de entrada
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
├── web/                   # Web support
│   ├── index.html
│   ├── manifest.json
│   └── icons/
├── pubspec.yaml           # Dependencias (actualizado)
└── README.md, ARCHITECTURE.md
```

## 📋 Antes de ejecutar

1. **Instalar Flutter 3.24+**
   ```bash
   # macOS/Linux
   git clone https://github.com/flutter/flutter.git -b stable

   # Agregar a PATH
   export PATH="$PATH:`pwd`/flutter/bin"

   # Windows: Descargar de https://flutter.dev/docs/get-started/install/windows
   ```

2. **Verificar instalación**
   ```bash
   flutter doctor
   ```

3. **Generar dependencias**
   ```bash
   cd mobile
   flutter pub get
   ```

## 🚀 Ejecutar

### Web (Chrome)
```bash
flutter run -d chrome
```

### Mobile (Android)
```bash
flutter run -d android
```

### Mobile (iOS)
```bash
flutter run -d ios
```

## 🔧 Configuración

- **API Base URL**: `lib/core/config.dart` - `AppConfig.apiBaseUrl`
- **Temas**: `lib/main.dart` - ColorScheme configuration
- **Rutas**: `lib/presentation/routes.dart`
- **Providers**: `lib/presentation/providers/providers.dart`

## 📝 Notas

- Todas las dependencias están actualizadas a versiones estables
- Compatible con Web, iOS y Android
- Usa Riverpod 2.0 para state management
- Secure storage para JWT tokens
- Manejo de errores con try-catch y .when()

## 🆘 Problemas comunes

### "API Client not initialized"
- Asegúrate de que `apiClientProvider` se inicializa primero
- Usa `ref.watch()` en lugar de `ref.read()` en UI

### Permisos denegados (Android/iOS)
- Verifica `AndroidManifest.xml` e `Info.plist`
- Usa `permission_handler` para solicitar

### WebSocket no conecta
- Verifica URL en `AppConfig.webSocketUrl()`
- Asegura que backend soporta WSS en HTTPS

## 📚 Recursos

- [Flutter Docs](https://flutter.dev/docs)
- [Riverpod Reference](https://riverpod.dev)
- [Dio Documentation](https://pub.dev/packages/dio)

---

**Proyecto listo para desarrollo. ¡Ejecuta flutter run -d chrome para comenzar!**
