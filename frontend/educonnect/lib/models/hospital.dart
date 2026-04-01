class Hospital {
  final int id;
  final String name;
  final String category;
  final String address;
  final int availableBeds;
  final String emergencyContact;
  final double rating;
  final double? distance;
  final String? image;

  Hospital({
    required this.id,
    required this.name,
    required this.category,
    required this.address,
    required this.availableBeds,
    required this.emergencyContact,
    required this.rating,
    this.distance,
    this.image,
  });

  factory Hospital.fromJson(Map<String, dynamic> json) {
    return Hospital(
      id: json['id'],
      name: json['name'],
      category: json['category'] ?? 'General',
      address: json['address'] ?? 'No address',
      availableBeds: json['available_beds'] ?? 0,
      emergencyContact: json['emergency_contact'] ?? 'N/A',
      rating: (json['rating'] ?? 0.0).toDouble(),
      distance: json['distance']?.toDouble(),
      image: json['image'],
    );
  }
}
