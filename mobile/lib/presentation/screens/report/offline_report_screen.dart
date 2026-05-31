import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:uuid/uuid.dart';

import '../../../data/local/offline_storage.dart';
import '../../../data/models/models.dart';
import '../../providers/providers.dart';

class OfflineReportScreen extends ConsumerStatefulWidget {
  const OfflineReportScreen({super.key});

  @override
  ConsumerState<OfflineReportScreen> createState() => _OfflineReportScreenState();
}

class _OfflineReportScreenState extends ConsumerState<OfflineReportScreen> {
  final _descriptionController = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<Position?> _getLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Activa el GPS para guardar la emergencia');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw Exception('Permiso de ubicación requerido');
    }

    return Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
  }

  Future<void> _save() async {
    final description = _descriptionController.text.trim();
    if (description.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Describe la emergencia')),
      );
      return;
    }

    setState(() => _saving = true);
    try {
      final position = await _getLocation();
      if (position == null) return;

      final formState = ref.read(reportFormProvider);
      final emergencia = EmergenciaLocal(
        id_local: const Uuid().v4(),
        descripcion: description,
        latitud: position.latitude,
        longitud: position.longitude,
        id_vehiculo: formState.selectedVehicleId,
        fecha_creacion: DateTime.now(),
      );

      await OfflineStorage.guardarEmergencia(emergencia);
      ref.invalidate(pendientesCountProvider);

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Emergencia guardada. Se sincronizara cuando tengas conexion.',
          ),
        ),
      );
      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceAll('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergencia offline')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _descriptionController,
            maxLines: 5,
            decoration: const InputDecoration(
              labelText: 'Descripción',
              hintText: 'Describe lo que ocurrió y cualquier referencia útil',
              prefixIcon: Icon(Icons.description_outlined),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'La ubicación y fecha se capturan automáticamente. No se hará ninguna llamada de red.',
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _saving ? null : _save,
            icon: _saving
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.save_outlined),
            label: Text(_saving ? 'Guardando...' : 'Guardar emergencia'),
          ),
        ],
      ),
    );
  }
}
