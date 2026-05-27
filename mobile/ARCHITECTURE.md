# Architecture - Emergencias Vehiculares Mobile

Documentación de la arquitectura de la aplicación Flutter.

## 🏛️ Patrón de Arquitectura: Clean Architecture + MVVM

```
Presentation Layer (MVVM + Riverpod)
        ↓
Providers Layer (State Management)
        ↓
Data Layer (Repositories + Models)
        ↓
Core Layer (HTTP, Config, Utils)
```

## 📊 Estructura detallada

### **Core Layer** 📦
Infraestructura base de la aplicación.

```
core/
├── api_client.dart       # Cliente HTTP con Dio + JWT
├── config.dart           # Configuración (URLs, timeouts)
├── constants.dart        # Constantes globales
└── extensions.dart       # Extensiones de Dart
```

**Responsabilidad:**
- Conectividad HTTP
- Almacenamiento seguro
- Configuración centralizada

### **Data Layer** 💾
Gestión de datos y comunicación con APIs.

```
data/
├── models/
│   └── models.dart       # DTOs y entidades
└── repositories/
    └── repositories.dart # Lógica de datos
```

**Modelos principales:**
- `User` - Usuario autenticado
- `Incident` - Incidente reportado
- `Vehicle` - Vehículo del usuario
- `Evidence` - Evidencias (fotos, audio, texto)
- `Assignment` - Asignación a taller
- `Notification` - Notificaciones en tiempo real

**Repositorios:**
- `AuthRepository` - Autenticación
- `IncidentRepository` - Gestión de incidentes
- `VehicleRepository` - Gestión de vehículos

### **Presentation Layer** 🎨
Interfaz de usuario y estado de componentes.

```
presentation/
├── routes.dart           # Rutas de navegación
├── providers/
│   └── providers.dart    # Providers Riverpod
└── screens/
    ├── splash/           # Pantalla de carga
    ├── auth/             # Login/Registro
    ├── home/             # Dashboard
    ├── report/           # Reporte de emergencia
    ├── incidents/        # Mis incidentes
    ├── map/              # Mapa en vivo
    └── profile/          # Perfil de usuario
```

### **Shared Layer** 🔄
Componentes reutilizables.

```
shared/
└── widgets.dart          # Widgets customizados
```

## 🌊 Flujo de datos

### Ejemplo: Reportar Emergencia

```
UI (ReportScreen)
    ↓
Riverpod Provider (reportStateProvider)
    ↓
Repository (IncidentRepository)
    ↓
API Client (Dio)
    ↓
Backend FastAPI
    ↓
Response ← UI updates
```

### Estado de autenticación

```
Provider: authStateProvider
├── AuthState
│   ├── isLoading
│   ├── isAuthenticated
│   ├── token (JWT)
│   └── error
└── AuthStateNotifier
    ├── login()
    ├── register()
    └── logout()
```

## 🔐 State Management con Riverpod

### Providers utilizados

```dart
// Simple Provider - Solo lectura
final apiClientProvider = FutureProvider<ApiClient>((ref) async { });

// State Notifier Provider - Con mutación
final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) { });

// Family Provider - Parametrizado
final incidentDetailProvider = FutureProvider.family<Incident, String>((ref, id) async { });
```

### Uso en UI

```dart
// Lectura
final incidents = ref.watch(myIncidentsProvider);

// Escuchar cambios
ref.listen(authStateProvider, (prev, next) {
  if (next.isAuthenticated) {
    // Navegar
  }
});

// Actualizar estado
ref.read(authStateProvider.notifier).login(...);
```

## 📱 Flujos principales de la app

### **Flujo de autenticación**

```
SplashScreen (2s delay)
    ↓
LoginScreen
    ├─ Email ──┐
    ├─ Password ├→ Repository.login()
    ├─ JWT Token saved in Secure Storage
    └→ HomeScreen
```

### **Flujo de reporte de emergencia**

```
HomeScreen
    ↓
ReportScreen
    ├─ GPS (Location)
    ├─ Fotos (ImagePicker)
    ├─ Audio (Recorder)
    ├─ Texto (TextField)
    └─ Submit
        ↓
    Repository.reportIncident()
        ↓
    Backend (multipart/form-data)
        ↓
    IncidentReportResponse
        ↓
    IncidentsScreen (tracking)
```

### **Flujo de seguimiento en tiempo real**

```
IncidentDetailScreen
    ↓
WebSocket Connection
    ├─ Connect: /ws/incidents/{id}
    ├─ Listen for updates
    └─ Update UI in real-time
        ├─ Estado: EN_CAMINO
        ├─ Técnico: ubicación
        └─ Estimado: tiempo
```

## 🔗 Conexiones de capas

### Presentation → Data

```dart
class ReportScreen {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportState = ref.watch(reportStateProvider);

    // Provider tiene acceso a Repository automáticamente
  }
}
```

### Data → Core

```dart
class IncidentRepository {
  final ApiClient apiClient;  // Inyección

  Future<List<Incident>> getMyIncidents() async {
    final response = await apiClient.get(...);
    return response.data.map((e) => Incident.fromJson(e)).toList();
  }
}
```

## 🧪 Manejo de errores

```dart
// En providers
.when(
  data: (data) => SuccessWidget(data),
  loading: () => LoadingWidget(),
  error: (error, stackTrace) => ErrorWidget(
    message: error.toString(),
    onRetry: () => ref.refresh(provider),
  ),
)

// En repositories
try {
  final response = await apiClient.get(...);
  return parseResponse(response);
} on DioException catch (e) {
  throw AppException(e.message);
}
```

## 📡 Integración Backend

**Endpoints utilizados:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /auth/register | Registro nuevo usuario |
| POST | /auth/login | Iniciar sesión |
| POST | /incidents/report | Reportar emergencia |
| GET | /incidents/my | Mis incidentes |
| GET | /incidents/{id} | Detalle incidente |
| GET | /vehicles | Mis vehículos |
| WS | /ws/incidents/{id} | Seguimiento en tiempo real |

## 🔒 Seguridad

1. **JWT Token**
   - Guardado en `FlutterSecureStorage`
   - Enviado en header `Authorization: Bearer {token}`

2. **Interceptores Dio**
   - Agrega token automáticamente
   - Maneja errores 401

3. **Validación**
   - Modelos con validation
   - HTTPException para errores de API

## 🚀 Deployment

```bash
# Build APK
flutter build apk --release

# Build iOS
flutter build ios --release

# Web (experimental)
flutter build web
```

## 🛠️ Debugging

```bash
# Logs de la app
flutter logs

# Profile de memoria
flutter run --profile

# DevTools
flutter pub global activate devtools
devtools
```

## 📚 Recursos

- [Flutter Docs](https://flutter.dev/docs)
- [Riverpod Docs](https://riverpod.dev)
- [Dio Docs](https://pub.dev/packages/dio)
- [Clean Architecture](https://resocoder.com/clean-architecture-tdd)

---

**Versión:** 1.0
**Actualizado:** 2026-04-05
