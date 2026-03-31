import 'package:flutter/material.dart';

class ReviewsPage extends StatelessWidget {
  const ReviewsPage({super.key});

  Widget reviewCard({
    required String category,
    required String title,
    required String review,
    required String date,
    required int rating,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// CATEGORY + DATE
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.purple.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(category,
                    style: const TextStyle(color: Colors.purple)),
              ),
              Text(date, style: const TextStyle(color: Colors.grey)),
            ],
          ),

          const SizedBox(height: 8),

          Text(title,
              style:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),

          const SizedBox(height: 6),

          /// ⭐ STARS
          Row(
            children: List.generate(
              5,
              (index) => Icon(
                index < rating ? Icons.star : Icons.star_border,
                color: Colors.orange,
                size: 18,
              ),
            ),
          ),

          const SizedBox(height: 6),

          Text(review),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text("My Reviews"),
      ),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text("2 reviews",
                style: TextStyle(color: Colors.grey)),
          ),

          reviewCard(
            category: "education",
            title: "St. Xavier's High School",
            rating: 5,
            review:
                "Excellent faculty and infrastructure. Highly recommended!",
            date: "2024-02-15",
          ),

          reviewCard(
            category: "stay",
            title: "Comfort Living PG",
            rating: 4,
            review:
                "Good amenities and clean rooms. Owner is very cooperative.",
            date: "2024-02-10",
          ),
        ],
      ),
    );
  }
}