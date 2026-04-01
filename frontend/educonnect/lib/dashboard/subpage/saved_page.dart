import 'package:flutter/material.dart';

class SavedListingsPage extends StatelessWidget {
  const SavedListingsPage({super.key});

  Widget savedCard(BuildContext context, {
    required String category,
    required String title,
    required String location,
    required String rating,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 8)],
      ),
      child: Row(
        children: [
          Container(
            width: 70,
            height: 70,
            decoration: BoxDecoration(
              color: Colors.deepPurple.withOpacity(0.1),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(
              Icons.bookmark_added,
              color: Colors.deepPurple,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  category.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.deepPurple,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined,
                        size: 14, color: Colors.grey),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        location,
                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.star, size: 14, color: Colors.orange),
                    const SizedBox(width: 4),
                    Text(rating, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.favorite, color: Colors.redAccent, size: 22),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("Saved Listings", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: isDark ? Colors.white : Colors.black,
      ),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 20, 16, 12),
            child: Text(
              "Your favorite places and bookmark markers",
              style: TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.w500),
            ),
          ),
          savedCard(
            context,
            category: "Education",
            title: "St. Xavier's High School",
            location: "Bangalore, Karnataka",
            rating: "4.8",
          ),
          savedCard(
            context,
            category: "Stay",
            title: "Comfort Living PG",
            location: "Koramangala, Bangalore",
            rating: "4.5",
          ),
          savedCard(
            context,
            category: "Medical",
            title: "Apollo Clinic",
            location: "Indiranagar, Bangalore",
            rating: "4.6",
          ),
        ],
      ),
    );
  }
}