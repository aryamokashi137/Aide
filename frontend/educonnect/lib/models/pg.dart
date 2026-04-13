class PG {
  final int id;
  final String name;
  final String address;
  final int rent;
  final bool foodIncluded;
  final String gender;
  final double rating;
  final double? distance;
  final String? image;
  final String? description;
  final String? facilities;

  PG({
    required this.id,
    required this.name,
    required this.address,
    required this.rent,
    required this.foodIncluded,
    required this.gender,
    required this.rating,
    this.distance,
    this.image,
    this.description,
    this.facilities,
  });

  factory PG.fromJson(Map<String, dynamic> json) {
    return PG(
      id: json['id'],
      name: json['name'],
      address: json['address'] ?? 'No address',
      rent: json['one_month_rent'] ?? 0,
      foodIncluded: json['food_included'] ?? false,
      gender: json['gender'] ?? 'Any',
      rating: (json['rating'] ?? 0.0).toDouble(),
      distance: json['distance']?.toDouble(),
      image: json['image'],
      description: json['description'],
      facilities: json['facilities'],
    );
  }
}
