import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/vehicle_models.dart';
import '../../providers/providers.dart';
import '../../../shared/widgets.dart';

class AddVehicleScreen extends ConsumerStatefulWidget {
  final Vehicle? existingVehicle;

  const AddVehicleScreen({super.key, this.existingVehicle});

  @override
  ConsumerState<AddVehicleScreen> createState() => _AddVehicleScreenState();
}

class _AddVehicleScreenState extends ConsumerState<AddVehicleScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _marcaController;
  late final TextEditingController _modeloController;
  late final TextEditingController _anioController;
  late final TextEditingController _placaController;

  bool get _isEditing => widget.existingVehicle != null;

  @override
  void initState() {
    super.initState();
    final v = widget.existingVehicle;
    _marcaController = TextEditingController(text: v?.marca ?? '');
    _modeloController = TextEditingController(text: v?.modelo ?? '');
    _anioController =
        TextEditingController(text: v?.anio?.toString() ?? '');
    _placaController = TextEditingController(text: v?.placa ?? '');
  }

  @override
  void dispose() {
    _marcaController.dispose();
    _modeloController.dispose();
    _anioController.dispose();
    _placaController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    final marca = _marcaController.text.trim();
    final modelo = _modeloController.text.trim();
    final anio = int.tryParse(_anioController.text.trim());
    final placa = _placaController.text.trim();

    bool success;
    if (_isEditing) {
      success = await ref.read(vehicleFormProvider.notifier).updateVehicle(
            int.parse(widget.existingVehicle!.idVehiculo),
            marca: marca,
            modelo: modelo,
            anio: anio,
            placa: placa,
          );
    } else {
      success = await ref.read(vehicleFormProvider.notifier).createVehicle(
            marca: marca,
            modelo: modelo,
            anio: anio,
            placa: placa,
          );
    }

    if (!mounted) return;
    if (success) {
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(vehicleFormProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar vehículo' : 'Agregar vehículo'),
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (formState.errorMessage != null) ...[
                AppErrorCard(message: formState.errorMessage!),
                const SizedBox(height: 16),
              ],
              AppTextField(
                controller: _marcaController,
                label: 'Marca',
                prefixIcon: Icons.badge_outlined,
              ),
              const SizedBox(height: 16),
              AppTextField(
                controller: _modeloController,
                label: 'Modelo',
                prefixIcon: Icons.directions_car_outlined,
              ),
              const SizedBox(height: 16),
              AppTextField(
                controller: _anioController,
                label: 'Año',
                keyboardType: TextInputType.number,
                prefixIcon: Icons.calendar_today_outlined,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) return null;
                  final anio = int.tryParse(value.trim());
                  if (anio == null) return 'Ingresá un año válido';
                  if (anio < 1900 || anio > 2100) return 'Año fuera de rango';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              AppTextField(
                controller: _placaController,
                label: 'Patente / Placa',
                prefixIcon: Icons.confirmation_number_outlined,
              ),
              const SizedBox(height: 28),
              AppButton(
                onPressed: formState.isLoading ? null : _save,
                isLoading: formState.isLoading,
                child: Text(
                  _isEditing ? 'Guardar cambios' : 'Registrar vehículo',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
