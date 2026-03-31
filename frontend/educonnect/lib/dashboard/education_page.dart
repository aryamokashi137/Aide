import 'package:educonnect/dashboard/subpage/EducationDetailsPage.dart';
import 'package:flutter/material.dart';

class EducationPage extends StatelessWidget {
  const EducationPage({super.key});

Widget institutionCard({
  required BuildContext context, 
  required String name,
  required String category,
  required String image,
  required String location,
  required String fees,
  required String rating,
}) {
  return GestureDetector(
    onTap: () {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => EducationDetailsPage(
            name: name,
            category: category,
            image: image,
            location: location,
            fees: fees,
            rating: rating,
          ),
        ),
      );
    },

    child: Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// IMAGE
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            child: Image.network(
              image,
              height: 160,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: category == "College"
                            ? Colors.blue.shade50
                            : Colors.green.shade50,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        category,
                        style: TextStyle(
                          color: category == "College"
                              ? Colors.blue
                              : Colors.green,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 6),
                Text("⭐ $rating"),
                const SizedBox(height: 6),

                Text(
                  location,
                  style: const TextStyle(color: Colors.grey),
                ),

                const SizedBox(height: 8),
                Text(
                  fees,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        /// SEARCH
        TextField(
          decoration: InputDecoration(
            hintText: "Search institutions...",
            prefixIcon: const Icon(Icons.search),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(30),
              borderSide: BorderSide.none,
            ),
          ),
        ),

        const SizedBox(height: 20),

        const Text(
          "5 institutions found",
          style: TextStyle(color: Colors.grey),
        ),

        const SizedBox(height: 16),

        /// SCHOOLS
        institutionCard(
          context: context,
          name: "St. Xavier's High School",
          category: "School",
          image:
              "https://images.unsplash.com/photo-1588072432836-e10032774350",
          location: "Koramangala, Bangalore",
          fees: "₹50,000 - ₹75,000/year",
          rating: "4.5 (234)",
        ),

        institutionCard(
          context: context,
          name: "Delhi Public School",
          category: "School",
          image:
              "https://images.unsplash.com/photo-1577896851231-70ef18881754",
          location: "Pune, Maharashtra",
          fees: "₹60,000 - ₹90,000/year",
          rating: "4.6 (310)",
        ),

        /// COLLEGES
        institutionCard(
          context: context,
          name: "Vishwakarma Institute of Technology (VIT)",
          category: "College",
          image:
              "https://images.unsplash.com/photo-1596495577886-d920f1fb7238",
          location: "Pune, Maharashtra",
          fees: "₹1.8L - ₹2.5L/year",
          rating: "4.7 (1.2k)",
        ),

        institutionCard(
          context: context,
          name: "MIT World Peace University",
          category: "College",
          image:
              "https://images.unsplash.com/photo-1562774053-701939374585",
          location: "Pune, Maharashtra",
          fees: "₹1.5L - ₹3L/year",
          rating: "4.4 (540)",
        ),

        institutionCard(
          context: context,
          name: "Christ University",
          category: "College",
          image:
              "https://images.unsplash.com/photo-1562774053-701939374585",
          location: "Bangalore, Karnataka",
          fees: "₹1.2L - ₹2.2L/year",
          rating: "4.5 (870)",
        ),
      ],
    );
  }
}