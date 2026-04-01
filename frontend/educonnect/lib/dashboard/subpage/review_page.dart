import 'package:flutter/material.dart';

class ReviewsPage extends StatelessWidget {
  const ReviewsPage({super.key});

  Widget reviewCard(BuildContext context, {
    required String category,
    required String title,
    required String review,
    required String date,
    required int rating,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 10)],
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
                  color: Colors.purple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(category,
                    style: const TextStyle(color: Colors.purple, fontWeight: FontWeight.bold, fontSize: 12)),
              ),
              Text(date, style: const TextStyle(color: Colors.grey, fontSize: 12)),
            ],
          ),

          const SizedBox(height: 12),

          Text(title,
              style:
                  const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),

          const SizedBox(height: 8),

          /// ⭐ STARS
          Row(
            children: List.generate(
              5,
              (index) => Icon(
                index < rating ? Icons.star : Icons.star_border,
                color: Colors.orange,
                size: 20,
              ),
            ),
          ),

          const SizedBox(height: 10),

          Text(review, style: TextStyle(color: isDark ? Colors.white70 : Colors.black87, height: 1.4)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("My Reviews", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black,
      ),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text("2 reviews found",
                style: TextStyle(color: Colors.grey, fontWeight: FontWeight.w600)),
          ),

          reviewCard(
            context,
            category: "EDUCATION",
            title: "St. Xavier's High School",
            rating: 5,
            review:
                "Excellent faculty and world-class infrastructure. My child is truly blossoming here. Highly recommended!",
            date: "2024-02-15",
          ),

          reviewCard(
            context,
            category: "STAY",
            title: "Comfort Living PG",
            rating: 4,
            review:
                "Very good amenities and properly clean rooms. The owner is cooperative and responds quickly to any issues.",
            date: "2024-02-10",
          ),
        ],
      ),
    );
  }
}