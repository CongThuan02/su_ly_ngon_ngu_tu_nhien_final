import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';

class ChatProvider extends ChangeNotifier {
  final ApiService _api;
  final String userId;
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  ChatProvider({required ApiService api, this.userId = 'default'}) : _api = api;

  List<ChatMessage> get messages => List.unmodifiable(_messages);
  bool get isLoading => _isLoading;

  Future<void> sendMessage(String text) async {
    _messages.add(ChatMessage(text: text, isUser: true));
    _isLoading = true;
    notifyListeners();

    try {
      final result = await _api.sendMessage(text, userId);
      final tasksList = (result['tasks'] as List<dynamic>?)
          ?.map((t) => Map<String, dynamic>.from(t as Map))
          .toList() ?? [];

      _messages.add(ChatMessage(
        text: result['response'] ?? 'Có lỗi xảy ra.',
        isUser: false,
        intent: result['intent'],
        confidence: (result['confidence'] as num?)?.toDouble(),
        source: result['source'],
        entities: result['entities'] as Map<String, dynamic>?,
        tasks: tasksList,
      ));
    } catch (e) {
      _messages.add(ChatMessage(
        text: 'Không thể kết nối server. Hãy kiểm tra lại.',
        isUser: false,
      ));
    }

    _isLoading = false;
    notifyListeners();
  }

  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }
}
