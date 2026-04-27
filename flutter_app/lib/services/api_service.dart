import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/task.dart';

class ApiService {
  final String baseUrl;

  // Đổi IP khi test trên thiết bị thật
  // localhost: simulator/emulator, IP máy: thiết bị thật
  ApiService({this.baseUrl = 'http://localhost:8000'});

  // === Chat ===
  Future<Map<String, dynamic>> sendMessage(String message, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message, 'user_id': userId}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    }
    throw Exception('Chat failed: ${response.statusCode}');
  }

  // === Tasks ===
  Future<List<Task>> getTasks(String userId) async {
    final response = await http.get(Uri.parse('$baseUrl/tasks/$userId'));
    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      final tasks = data['tasks'] as List;
      return tasks.map((t) => Task.fromJson(t)).toList();
    }
    throw Exception('Get tasks failed: ${response.statusCode}');
  }

  Future<void> createTask(String title, String userId, {String? dueTime}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/tasks'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'title': title,
        'user_id': userId,
        'due_time': dueTime,
      }),
    );
    if (response.statusCode != 200) {
      throw Exception('Create task failed: ${response.statusCode}');
    }
  }

  Future<void> completeTask(String taskId) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/tasks/$taskId/complete'),
    );
    if (response.statusCode != 200) {
      throw Exception('Complete task failed: ${response.statusCode}');
    }
  }

  Future<void> deleteTask(String taskId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/tasks/$taskId'),
    );
    if (response.statusCode != 200) {
      throw Exception('Delete task failed: ${response.statusCode}');
    }
  }
}
