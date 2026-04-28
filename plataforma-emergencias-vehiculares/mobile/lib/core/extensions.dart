import 'package:intl/intl.dart';

extension StringExtensions on String {
  String get capitalize =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';

  bool get isValidEmail {
    final emailRegex =
        RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    return emailRegex.hasMatch(this);
  }

  String get withoutException => replaceAll('Exception: ', '');
}

extension DateTimeExtensions on DateTime {
  String get formatted => DateFormat('dd/MM/yyyy HH:mm').format(this);
  String get dateOnly => DateFormat('dd/MM/yyyy').format(this);

  String get relative {
    final now = DateTime.now();
    final diff = now.difference(this);
    if (diff.inMinutes < 1) return 'Hace un momento';
    if (diff.inMinutes < 60) return 'Hace ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'Hace ${diff.inHours} h';
    if (diff.inDays < 7) return 'Hace ${diff.inDays} días';
    return dateOnly;
  }
}
