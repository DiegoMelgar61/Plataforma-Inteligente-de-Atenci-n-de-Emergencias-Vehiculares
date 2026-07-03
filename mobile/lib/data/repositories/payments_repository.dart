import 'dart:io';

import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../models/payment_models.dart';

// ── Payments ──────────────────────────────────────────────────────────────────

class PaymentsRepository {
  final ApiClient _client;
  PaymentsRepository(this._client);

  Future<List<Payment>> listarMisPagos() async {
    try {
      final response = await _client.dio.get('/payments/my');
      final data = response.data as List<dynamic>;
      return data
          .map((e) => Payment.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al cargar pagos';
      throw Exception(detail);
    }
  }

  Future<Payment> marcarComoPagado(
    int idPago,
    File comprobante, {
    String? notas,
  }) async {
    try {
      final fileName = comprobante.path.split('/').last.split('\\').last;
      final formData = FormData.fromMap({
        'comprobante': await MultipartFile.fromFile(
          comprobante.path,
          filename: fileName,
        ),
        if (notas != null && notas.isNotEmpty) 'notas_cliente': notas,
      });
      final response = await _client.dio.post(
        '/payments/$idPago/mark-paid',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      return Payment.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final detail =
          (e.response?.data as Map?)?['detail'] ?? 'Error al registrar pago';
      throw Exception(detail);
    }
  }
}
