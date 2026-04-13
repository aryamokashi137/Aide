class Hospital {
  final int id;
  final String name;
  final String category;
  final String address;
  final int availableBeds;
  final int icuBeds;
  final String emergencyContact;
  final String? phoneNumber;
  final String? email;
  final String? website;
  final String? googleMapsLink;
  final double rating;
  final double? distance;
  final String? image;

  Hospital({
    required this.id,
    required this.name,
    required this.category,
    required this.address,
    required this.availableBeds,
    required this.icuBeds,
    required this.emergencyContact,
    this.phoneNumber,
    this.email,
    this.website,
    this.googleMapsLink,
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
      icuBeds: json['icu_beds'] ?? 0,
      emergencyContact: json['emergency_contact'] ?? 'N/A',
      phoneNumber: json['phone_number'],
      email: json['email'],
      website: json['website'],
      googleMapsLink: json['google_maps_link'],
      rating: (json['rating'] ?? 0.0).toDouble(),
      distance: json['distance']?.toDouble(),
      image: json['image'],
    );
  }
}
