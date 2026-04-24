class Task {
  final String id;
  final String title;
  final String description;
  final String? dueTime;
  final bool isCompleted;
  final String? createdAt;

  Task({
    required this.id,
    required this.title,
    this.description = '',
    this.dueTime,
    this.isCompleted = false,
    this.createdAt,
  });

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      dueTime: json['due_time'],
      isCompleted: json['is_completed'] ?? false,
      createdAt: json['created_at']?.toString(),
    );
  }
}
