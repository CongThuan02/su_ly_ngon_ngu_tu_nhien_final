import 'package:flutter/material.dart';
import '../models/task.dart';
import '../services/api_service.dart';

class TaskProvider extends ChangeNotifier {
  final ApiService _api;
  final String userId;
  List<Task> _tasks = [];
  bool _isLoading = false;

  TaskProvider({required ApiService api, this.userId = 'default'}) : _api = api;

  List<Task> get tasks => List.unmodifiable(_tasks);
  List<Task> get pendingTasks => _tasks.where((t) => !t.isCompleted).toList();
  List<Task> get completedTasks => _tasks.where((t) => t.isCompleted).toList();
  bool get isLoading => _isLoading;

  Future<void> loadTasks() async {
    _isLoading = true;
    notifyListeners();
    try {
      _tasks = await _api.getTasks(userId);
    } catch (e) {
      debugPrint('Load tasks error: $e');
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> addTask(String title, {String? dueTime}) async {
    await _api.createTask(title, userId, dueTime: dueTime);
    await loadTasks();
  }

  Future<void> completeTask(String taskId) async {
    await _api.completeTask(taskId);
    await loadTasks();
  }

  Future<void> deleteTask(String taskId) async {
    await _api.deleteTask(taskId);
    await loadTasks();
  }
}
