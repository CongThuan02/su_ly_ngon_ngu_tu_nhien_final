class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? intent;
  final double? confidence;
  final String? source;
  final Map<String, dynamic>? entities;

  ChatMessage({
    required this.text,
    required this.isUser,
    DateTime? timestamp,
    this.intent,
    this.confidence,
    this.source,
    this.entities,
  }) : timestamp = timestamp ?? DateTime.now();
}
