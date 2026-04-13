class Review {
  final int id;
  final String content;
  final int rating;
  final String userName;
  final String entityName;
  final String entityType;
  final DateTime createdAt;

  Review({
    required this.id,
    required this.content,
    required this.rating,
    required this.userName,
    required this.entityName,
    required this.entityType,
    required this.createdAt,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'],
      content: json['content'],
      rating: json['rating'],
      userName: json['user_name'] ?? "Anonymous User",
      entityName: json['entity_name'] ?? "Unknown Entity",
      entityType: json['entity_type'] ?? "unknown",
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
