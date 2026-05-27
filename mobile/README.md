# Frontend Flutter - Emergencias Vehiculares

Aplicación móvil Flutter para clientes de la Plataforma Inteligente de Atención de Emergencias Vehiculares.

## ✨ Características principales

- ✅ **Autenticación JWT** con almacenamiento seguro
- ✅ **Reporte multimodal** (fotos, audio, texto + GPS)
- ✅ **Seguimiento en tiempo real** de incidentes con WebSocket
- ✅ **Gestión de vehículos** (registrar, listar)
- ✅ **Mis incidentes** con estado actualizado
- ✅ **Material Design 3** y soporte dark mode
- ✅ **State management** con Riverpod 2.0
- ✅ **Manejo de permisos** (ubicación, cámara, micrófono)

## 🏗️ Estructura de carpetas

```
lib/
├── main.dart                          # Punto de entrada
├── core/
│   ├── api_client.dart               # Cliente HTTP con Dio
│   ├── config.dart                   # Configuración global
│   ├── constants.dart                # Constantes
│   └── extensions.dart               # Extensiones útiles
├── data/
│   ├── models/
│   │   └── models.dart               # Modelos de datos
│   └── repositories/
│       └── repositories.dart         # Repositorios (API)
├── presentation/
│   ├── routes.dart                   # Rutas de navegación
│   ├── providers/
│   │   └── providers.dart            # Providers Riverpod
│   └── screens/
│       ├── splash/
│       ├── auth/
│       ├── home/
│       ├── report/
│       ├── incidents/
│       ├── map/
│       └── profile/
└── shared/
    └── widgets.dart                  # Widgets reutilizables
```

## 📋 Requerimiientos

- Flutter 3.24+
- Dart 3.0+
- Android API 21+ / iOS 11+

## 🚀 Instalación y uso

### 1. Clonar el repositorio
```bash
cd mobile
flutter pub get
```

### 2. Generar código (Riverpod)
```bash
flutter pub run build_runner build
```

### 3. Ejecutar la app
```bash
# Flutter 3.24+ con null safety
flutter run

# O especificar dispositivo
flutter run -d <device_id>
```

## 🔌 Conexión con Backend

Cambiar la URL del backend en `lib/core/config.dart`:

```dart
static const String apiBaseUrl = 'http://127.0.0.1:8000';  // Desarrollo
// static const String apiBaseUrl = 'https://emergencias.com';  // Producción
```

## 📱 Pantallas

### 1. **Splash**
- Logo de la app
- Delay de 2 segundos → Login

### 2. **Login/Registro**
- Email + contraseña
- Rol fijo: CLIENTE
- JWT token guardado en secure storage

### 3. **Home (Dashboard)**
- Botón grande "Reportar Emergencia"
- Links a mis incidentes y perfil
- Cards informativos

### 4. **Reportar Emergencia**
- Ubicación automática con GPS
- Seleccionar vehículo
- Cargar múltiples fotos
- Grabar/subir audio
- Descripción en texto
- Envío multipart al backend

### 5. **Mis Incidentes**
- Lista de incidentes reportados
- Estado en tiempo real (PENDIENTE, CLASIFICADO, ASIGNADO, EN_CAMINO, ATENDIDO, etc.)
- Filtros por estado
- Detalle con evidencias

### 6. **Perfil**
- Datos del usuario
- Mis vehículos
- Opción agregar vehículo
- Botón logout

## 🔐 Seguridad

- **JWT** almacenado en `FlutterSecureStorage`
- **Interceptores Dio** para agregar token automáticamente
- **Headers** Content-Type: application/json
- **Timeout** de conexión: 30 segundos

## 🌐 Conectividad WebSocket

Para seguimiento en tiempo real (opcional):
```dart
final wsUrl = AppConfig.webSocketUrl(incidentId);
// Conectar con web_socket_channel
```

## 📦 Dependencias principales

| Package | Versión | Uso |
|---------|---------|-----|
| flutter_riverpod | 2.4.0 | State management |
| dio | 5.3.0 | HTTP client |
| flutter_secure_storage | 9.0.0 | Storage seguro |
| geolocator | 10.1.0 | GPS |
| google_maps_flutter | 2.5.0 | Mapas |
| image_picker | 1.0.4 | Fotos/galería |
| record | 4.4.4 | Grabación audio |
| web_socket_channel | 2.4.0 | WebSocket |

## 🧪 Testing

```bash
# Tests unitarios
flutter test

# Cobertura
flutter test --coverage
```

## 📖 Notas de desarrollo

### Estado Management (Riverpod)
```dart
// Usar providers
final incidents = ref.watch(myIncidentsProvider);

// Escuchar cambios
ref.listen(authStateProvider, (prev, next) { });

// Actualizar Estado
ref.read(authStateProvider.notifier).login(...);
```

### Error Handling
```dart
// Capturar errores Dio
try {
  await apiClient.post(...);
} on DioException catch (e) {
  // Manejar error
}
```

### Migraciones (si usas Riverpod Code Gen)
```bash
flutter pub run build_runner watch
```

## 🐛 Troubleshooting

### "API Client not initialized"
- Asegúrate que el provider `apiClientProvider` se inicializa primero
- Usa `ref.watch()` en lugar de `ref.read()`

### Permisos denegados
- Agregar permisos en `AndroidManifest.xml` y `Info.plist`
- Usar `permission_handler` para solicitar

### WebSocket no conecta
- Verificar URL en `AppConfig.webSocketUrl()`
- Asegurar que backend soporta WSS en HTTPS

## 🎯 Próximas mejoras

- [ ] Pago en la app (Stripe/PayPal)
- [ ] Notificaciones push (Firebase Cloud Messaging)
- [ ] Chat con técnico
- [ ] Historial de gastos
- [ ] Suscripciones
- [ ] Integraciones de insurance

## 📞 Soporte

Para preguntas o reportar bugs, contacta con el equipo de desarrollo.

---

**Hecho con ❤️ por el equipo de Emergencias Vehiculares**
