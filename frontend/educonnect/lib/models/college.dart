class College {
  final int id;
  final String name;
  final String type;
  final String address;
  final String fees;
  final double rating;
  final double? distance;
  final String? image;
  final String? description;
  final String? streamsAvailable;
  final String? coursesOffered;

  College({
    required this.id,
    required this.name,
    required this.type,
    required this.address,
    required this.fees,
    required this.rating,
    this.distance,
    this.image,
    this.description,
    this.streamsAvailable,
    this.coursesOffered,
  });

  factory College.fromJson(Map<String, dynamic> json) {
    // Dynamically handle different 'fees' field names from the backend
    String displayFees = 'N/A';
    if (json.containsKey('fees') && json['fees'] != null) {
      displayFees = json['fees'].toString();
    } else if (json.containsKey('average_fees') && json['average_fees'] != null) {
      displayFees = json['average_fees'].toString();
    } else if (json.containsKey('monthly_charges') && json['monthly_charges'] != null) {
      displayFees = json['monthly_charges'].toString();
    } else if (json.containsKey('avg_monthly_price') && json['avg_monthly_price'] != null) {
      displayFees = json['avg_monthly_price'].toString();
    }

    return College(
      id: json['id'],
      name: json['name'] ?? 'Unknown Name',
      type: json['type'] ?? json['meal_types'] ?? json['coaching_type'] ?? 'Education',
      address: json['address'] ?? 'Location not specified',
      fees: displayFees,
      rating: (json['rating'] ?? json['hygiene_rating'] ?? 0.0).toDouble(),
      distance: json['distance']?.toDouble(),
      image: json['image'],
      description: json['description'],
      streamsAvailable: json['streams_available'],
      coursesOffered: json['courses_offered'],
    );
  }
}
