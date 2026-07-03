import 'package:flutter_riverpod/flutter_riverpod.dart';

// ── WS Notifications (global list) ───────────────────────────────────────────

class NotificationsNotifier extends StateNotifier<List<Map<String, dynamic>>> {
  NotificationsNotifier() : super(const []);

  void add(Map<String, dynamic> notification) {
    state = [notification, ...state];
  }

  void clear() => state = const [];
}

final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, List<Map<String, dynamic>>>(
  (ref) => NotificationsNotifier(),
);
