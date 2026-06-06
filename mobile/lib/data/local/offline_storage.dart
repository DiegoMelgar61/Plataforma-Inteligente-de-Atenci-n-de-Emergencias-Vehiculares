import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/models.dart';

class OfflineStorage {
  static const String _key = 'emergencias_offline';

  static Future<void> guardarEmergencia(EmergenciaLocal e) async {
    final emergencias = await obtenerTodas();
    emergencias.add(e);
    await _guardarTodas(emergencias);
  }

  static Future<List<EmergenciaLocal>> obtenerPendientes() async {
    final emergencias = await obtenerTodas();
    return emergencias.where((e) => !e.sincronizado).toList();
  }

  static Future<List<EmergenciaLocal>> obtenerTodas() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null || raw.isEmpty) return [];

    final decoded = jsonDecode(raw) as List<dynamic>;
    return decoded
        .map((item) => EmergenciaLocal.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  static Future<void> marcarSincronizada(String id_local) async {
    final emergencias = await obtenerTodas();
    for (final emergencia in emergencias) {
      if (emergencia.id_local == id_local) {
        emergencia.sincronizado = true;
        emergencia.error_sync = null;
      }
    }
    await _guardarTodas(emergencias);
  }

  static Future<void> marcarError(String id_local, String error) async {
    final emergencias = await obtenerTodas();
    for (final emergencia in emergencias) {
      if (emergencia.id_local == id_local) {
        emergencia.error_sync = error;
      }
    }
    await _guardarTodas(emergencias);
  }

  static Future<void> eliminarSincronizadas() async {
    final emergencias = await obtenerTodas();
    await _guardarTodas(
      emergencias.where((e) => !e.sincronizado).toList(),
    );
  }

  static Future<void> _guardarTodas(List<EmergenciaLocal> emergencias) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key,
      jsonEncode(emergencias.map((e) => e.toJson()).toList()),
    );
  }
}
