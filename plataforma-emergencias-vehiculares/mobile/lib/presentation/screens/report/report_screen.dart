import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import '../../../core/constants.dart';
import '../../../core/extensions.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';

class ReportScreen extends ConsumerStatefulWidget {
  const ReportScreen({super.key});

  @override
  ConsumerState<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends ConsumerState<ReportScreen> {
  final _descriptionController = TextEditingController();
  final _locationController = TextEditingController();
  bool _loadingLocation = false;

  @override
  void initState() {
    super.initState();
    _descriptionController.addListener(() {
      ref
          .read(reportFormProvider.notifier)
          .setDescription(_descriptionController.text);
    });
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  Future<void> _getLocation() async {
    setState(() => _loadingLocation = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Activa el GPS para obtener tu ubicación')),
          );
        }
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) return;
      }
      if (permission == LocationPermission.deniedForever) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Permiso de ubicación denegado permanentemente')),
          );
        }
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      ref
          .read(reportFormProvider.notifier)
          .setLocation(position.latitude, position.longitude);
      _locationController.text =
          '${position.latitude.toStringAsFixed(6)}, ${position.longitude.toStringAsFixed(6)}';
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al obtener ubicación: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _loadingLocation = false);
    }
  }

  Future<void> _pickFromCamera() async {
    final picker = ImagePicker();
    final photo = await picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 80,
    );
    if (photo != null) {
      ref.read(reportFormProvider.notifier).addFile(photo.path);
    }
  }

  Future<void> _pickFromGallery() async {
    final picker = ImagePicker();
    final images = await picker.pickMultiImage(imageQuality: 80);
    for (final image in images) {
      ref.read(reportFormProvider.notifier).addFile(image.path);
    }
  }

  Future<void> _pickFiles() async {
    final result = await FilePicker.platform.pickFiles(
      allowMultiple: true,
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'],
    );
    if (result != null) {
      for (final file in result.files) {
        if (file.path != null) {
          ref.read(reportFormProvider.notifier).addFile(file.path!);
        }
      }
    }
  }

  void _showPickerOptions() {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined),
              title: const Text('Tomar foto'),
              onTap: () {
                Navigator.pop(ctx);
                _pickFromCamera();
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Galería de imágenes'),
              onTap: () {
                Navigator.pop(ctx);
                _pickFromGallery();
              },
            ),
            ListTile(
              leading: const Icon(Icons.attach_file_outlined),
              title: const Text('Seleccionar archivo'),
              onTap: () {
                Navigator.pop(ctx);
                _pickFiles();
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    final success = await ref.read(reportFormProvider.notifier).submit();
    if (!mounted) return;
    if (success) {
      ref.invalidate(myIncidentsProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Emergencia reportada exitosamente'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(reportFormProvider);
    final vehiclesAsync = ref.watch(vehiclesProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reportar Emergencia'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Info card
            Card(
              color: colorScheme.errorContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: colorScheme.onErrorContainer),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Completa el formulario con los detalles de tu emergencia. '
                        'Un taller será asignado a la brevedad.',
                        style: TextStyle(color: colorScheme.onErrorContainer),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            if (formState.errorMessage != null) ...[
              AppErrorCard(message: formState.errorMessage!),
              const SizedBox(height: 16),
            ],

            // Vehicle selector
            Text(
              'Vehículo *',
              style: Theme.of(context)
                  .textTheme
                  .labelLarge
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            vehiclesAsync.when(
              loading: () => const AppLoadingIndicator(
                  message: 'Cargando vehículos...'),
              error: (error, _) => AppErrorCard(
                message: 'Error al cargar vehículos: ${error.toString().withoutException}',
                onRetry: () => ref.invalidate(vehiclesProvider),
              ),
              data: (vehicles) {
                if (vehicles.isEmpty) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Icon(Icons.directions_car_outlined,
                              size: 40, color: colorScheme.outlineVariant),
                          const SizedBox(height: 8),
                          const Text(
                            'No tienes vehículos registrados',
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  );
                }
                return DropdownButtonFormField<String>(
                  value: formState.selectedVehicleId,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    filled: true,
                    prefixIcon: Icon(Icons.directions_car_outlined),
                    hintText: 'Selecciona un vehículo',
                  ),
                  items: vehicles
                      .map(
                        (v) => DropdownMenuItem(
                          value: v.idVehiculo,
                          child: Text(v.displayName, overflow: TextOverflow.ellipsis),
                        ),
                      )
                      .toList(),
                  onChanged: (id) =>
                      ref.read(reportFormProvider.notifier).setVehicle(id),
                );
              },
            ),
            const SizedBox(height: 16),

            // Description
            Text(
              'Descripción de la emergencia *',
              style: Theme.of(context)
                  .textTheme
                  .labelLarge
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            AppTextField(
              controller: _descriptionController,
              label: 'Descripción',
              hint:
                  'Ej: Llanta ponchada en autopista, motor recalentado, etc.',
              maxLines: 4,
              prefixIcon: Icons.description_outlined,
            ),
            const SizedBox(height: 16),

            // Location
            Text(
              'Ubicación',
              style: Theme.of(context)
                  .textTheme
                  .labelLarge
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: AppTextField(
                    controller: _locationController,
                    label: 'Coordenadas GPS',
                    readOnly: true,
                    prefixIcon: Icons.location_on_outlined,
                  ),
                ),
                const SizedBox(width: 10),
                FilledButton.icon(
                  onPressed: _loadingLocation ? null : _getLocation,
                  icon: _loadingLocation
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.my_location),
                  label: const Text('Obtener'),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Evidence
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Evidencia (fotos / archivos)',
                  style: Theme.of(context)
                      .textTheme
                      .labelLarge
                      ?.copyWith(fontWeight: FontWeight.w600),
                ),
                TextButton.icon(
                  onPressed: _showPickerOptions,
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Agregar'),
                ),
              ],
            ),
            if (formState.filePaths.isNotEmpty) ...[
              const SizedBox(height: 8),
              SizedBox(
                height: 90,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: formState.filePaths.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final path = formState.filePaths[index];
                    final isImage = path.toLowerCase().endsWith('.jpg') ||
                        path.toLowerCase().endsWith('.jpeg') ||
                        path.toLowerCase().endsWith('.png');
                    return Stack(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: isImage
                              ? Image.file(
                                  File(path),
                                  width: 90,
                                  height: 90,
                                  fit: BoxFit.cover,
                                )
                              : Container(
                                  width: 90,
                                  height: 90,
                                  color: colorScheme.surfaceContainerHighest,
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.insert_drive_file_outlined,
                                          color: colorScheme.primary),
                                      const SizedBox(height: 4),
                                      Text(
                                        path.split('/').last.split('\\').last,
                                        style: Theme.of(context)
                                            .textTheme
                                            .labelSmall,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        textAlign: TextAlign.center,
                                      ),
                                    ],
                                  ),
                                ),
                        ),
                        Positioned(
                          top: 2,
                          right: 2,
                          child: GestureDetector(
                            onTap: () =>
                                ref.read(reportFormProvider.notifier).removeFile(path),
                            child: Container(
                              decoration: BoxDecoration(
                                color: colorScheme.error,
                                shape: BoxShape.circle,
                              ),
                              padding: const EdgeInsets.all(2),
                              child: Icon(Icons.close,
                                  size: 14, color: colorScheme.onError),
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ] else
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  border: Border.all(
                      color: colorScheme.outlineVariant,
                      style: BorderStyle.solid),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Column(
                    children: [
                      Icon(Icons.add_photo_alternate_outlined,
                          size: 36, color: colorScheme.outlineVariant),
                      const SizedBox(height: 8),
                      Text(
                        'Sin archivos adjuntos',
                        style: TextStyle(color: colorScheme.outlineVariant),
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 32),

            AppButton(
              onPressed: formState.isSubmitting ? null : _submit,
              isLoading: formState.isSubmitting,
              child: const Text(
                'Enviar reporte de emergencia',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
