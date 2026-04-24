class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? intent;
  final double? confidence;
  final String? source;
  final Map<String, dynamic>? entities;
  final List<Map<String, dynamic>> tasks;

  ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
    this.intent,
    this.confidence,
    this.source,
    this.entities,
    this.tasks = const [],
  }) : timestamp = timestamp ?? DateTime.now();
}
