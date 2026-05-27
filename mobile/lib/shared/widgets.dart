import 'package:flutter/material.dart';
import '../core/extensions.dart';
import '../data/models/models.dart';

// ── Loading ───────────────────────────────────────────────────────────────────

class AppLoadingIndicator extends StatelessWidget {
  final String? message;
  const AppLoadingIndicator({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(message!, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ],
      ),
    );
  }
}

// ── Error card ────────────────────────────────────────────────────────────────

class AppErrorCard extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const AppErrorCard({super.key, required this.message, this.onRetry});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      color: colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: colorScheme.onErrorContainer),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: TextStyle(color: colorScheme.onErrorContainer),
              ),
            ),
            if (onRetry != null)
              TextButton(
                onPressed: onRetry,
                child: const Text('Reintentar'),
              ),
          ],
        ),
      ),
    );
  }
}

// ── Empty state ───────────────────────────────────────────────────────────────

class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget? action;

  const EmptyStateWidget({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 72, color: colorScheme.outlineVariant),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(
                subtitle!,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colorScheme.outlineVariant,
                    ),
              ),
            ],
            if (action != null) ...[
              const SizedBox(height: 24),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}

// ── Text field ────────────────────────────────────────────────────────────────

class AppTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String? hint;
  final TextInputType? keyboardType;
  final bool obscureText;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final String? Function(String?)? validator;
  final int maxLines;
  final bool readOnly;
  final VoidCallback? onTap;
  final void Function(String)? onChanged;

  const AppTextField({
    super.key,
    required this.controller,
    required this.label,
    this.hint,
    this.keyboardType,
    this.obscureText = false,
    this.prefixIcon,
    this.suffixIcon,
    this.validator,
    this.maxLines = 1,
    this.readOnly = false,
    this.onTap,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      maxLines: maxLines,
      readOnly: readOnly,
      onTap: onTap,
      onChanged: onChanged,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: prefixIcon != null ? Icon(prefixIcon) : null,
        suffixIcon: suffixIcon,
        border: const OutlineInputBorder(),
        filled: true,
      ),
    );
  }
}

// ── Button ────────────────────────────────────────────────────────────────────

class AppButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final bool isLoading;
  final bool isOutlined;

  const AppButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.isLoading = false,
    this.isOutlined = false,
  });

  @override
  Widget build(BuildContext context) {
    final content = isLoading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          )
        : child;

    if (isOutlined) {
      return SizedBox(
        width: double.infinity,
        height: 52,
        child: OutlinedButton(onPressed: onPressed, child: content),
      );
    }

    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(onPressed: onPressed, child: content),
    );
  }
}

// ── Status chip ───────────────────────────────────────────────────────────────

class StatusChip extends StatelessWidget {
  final String status;
  const StatusChip({super.key, required this.status});

  String get _normalized => status.toUpperCase();

  Color _bgColor(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    switch (_normalized) {
      case 'PENDIENTE':
        return Colors.orange.shade100;
      case 'EN_PROCESO_IA':
      case 'CLASIFICADO':
        return Colors.blue.shade100;
      case 'ASIGNADO':
      case 'EN_CAMINO':
        return Colors.indigo.shade100;
      case 'EN_PROCESO':
        return Colors.purple.shade100;
      case 'ATENDIDO':
        return Colors.green.shade100;
      case 'CANCELADO':
      case 'INCIERTO':
        return colorScheme.errorContainer;
      default:
        return colorScheme.surfaceContainerHighest;
    }
  }

  Color _fgColor(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    switch (_normalized) {
      case 'PENDIENTE':
        return Colors.orange.shade900;
      case 'EN_PROCESO_IA':
      case 'CLASIFICADO':
        return Colors.blue.shade900;
      case 'ASIGNADO':
      case 'EN_CAMINO':
        return Colors.indigo.shade900;
      case 'EN_PROCESO':
        return Colors.purple.shade900;
      case 'ATENDIDO':
        return Colors.green.shade900;
      case 'CANCELADO':
      case 'INCIERTO':
        return colorScheme.onErrorContainer;
      default:
        return colorScheme.onSurfaceVariant;
    }
  }

  String get _label {
    switch (_normalized) {
      case 'PENDIENTE':
        return 'Pendiente';
      case 'EN_PROCESO_IA':
        return 'Procesando IA';
      case 'CLASIFICADO':
        return 'Clasificado';
      case 'ASIGNADO':
        return 'Asignado';
      case 'EN_CAMINO':
        return 'En camino';
      case 'EN_PROCESO':
        return 'En proceso';
      case 'ATENDIDO':
        return 'Atendido';
      case 'CANCELADO':
        return 'Cancelado';
      case 'INCIERTO':
        return 'Incierto';
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _bgColor(context),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        _label,
        style: TextStyle(
          color: _fgColor(context),
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

// ── Incident card ─────────────────────────────────────────────────────────────

class IncidentCard extends StatelessWidget {
  final Incident incident;
  final VoidCallback? onTap;

  const IncidentCard({super.key, required this.incident, this.onTap});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    radius: 20,
                    backgroundColor: colorScheme.primaryContainer,
                    child: Icon(
                      Icons.car_crash,
                      size: 20,
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${incident.clasificacionLabel} — #${incident.idIncidente.substring(0, 8)}',
                          style:
                              Theme.of(context).textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                        ),
                        Text(
                          incident.fechaCreacion?.relative ?? '',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                        ),
                      ],
                    ),
                  ),
                  StatusChip(status: incident.estado),
                ],
              ),
              const SizedBox(height: 8),
              // Priority + classification info
              Row(
                children: [
                  Icon(Icons.flag_outlined,
                      size: 14, color: colorScheme.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Text(
                    'Prioridad: ${incident.prioridadLabel}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
              if (incident.latitud != null && incident.longitud != null) ...[
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(
                      Icons.location_on_outlined,
                      size: 14,
                      color: colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${incident.latitud!.toStringAsFixed(4)}, '
                      '${incident.longitud!.toStringAsFixed(4)}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                    ),
                  ],
                ),
              ],
              if (incident.resumenIa != null) ...[
                const SizedBox(height: 6),
                Text(
                  incident.resumenIa!,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
