import 'package:flutter/material.dart';

class MedicalPage extends StatelessWidget {
  const MedicalPage({super.key});

  Widget _serviceCategory(BuildContext context, String title, IconData icon, Color color) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      width: 100,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: color.withOpacity(isDark ? 0.2 : 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87)),
        ],
      ),
    );
  }

  Widget _hospitalCard(BuildContext context, {
    required String name,
    required String image,
    required String rating,
    required String location,
    required String distance,
    required int beds,
  }) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 10)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                child: Image.network(
                  image,
                  height: 180, width: double.infinity, fit: BoxFit.cover,
                  errorBuilder: (_,__,___) => Container(height: 180, color: Colors.grey.shade900, child: const Icon(Icons.broken_image_outlined)),
                ),
              ),
              Positioned(
                top: 12, right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(color: isDark ? Colors.black87 : Colors.white, borderRadius: BorderRadius.circular(20)),
                  child: Text(distance, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black)),
                ),
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.star_outline, color: Colors.orange, size: 18),
                    const SizedBox(width: 4),
                    Text(rating, style: const TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(width: 10),
                    const Icon(Icons.location_on_outlined, color: Colors.grey, size: 16),
                    const SizedBox(width: 4),
                    Expanded(child: Text(location, style: const TextStyle(color: Colors.grey, fontSize: 13), overflow: TextOverflow.ellipsis)),
                  ],
                ),
                const SizedBox(height: 15),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("Available Beds", style: TextStyle(color: Colors.grey, fontSize: 12)),
                        Text(beds.toString(), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.green)),
                      ],
                    ),
                    ElevatedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.call_outlined, size: 16),
                      label: const Text("Emergency"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red.withOpacity(0.1),
                        foregroundColor: Colors.red,
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("Medical Services", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            /// QUICK SERVICES
            const Text("Quick Services", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _serviceCategory(context, "Hospitals", Icons.local_hospital_outlined, Colors.red),
                  _serviceCategory(context, "Doctors", Icons.person_search_outlined, Colors.blue),
                  _serviceCategory(context, "Blood Bank", Icons.bloodtype_outlined, Colors.redAccent),
                  _serviceCategory(context, "Ambulance", Icons.airport_shuttle_outlined, Colors.orange),
                ],
              ),
            ),

            const SizedBox(height: 30),

            /// HOSPITALS
            const Text("Nearby Hospitals", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            
            _hospitalCard(
              context,
              name: "City Care General Hospital",
              image: "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d",
              rating: "4.8",
              location: "MG Road, Central District",
              distance: "1.2 km",
              beds: 45,
            ),
            
            _hospitalCard(
              context,
              name: "St. Luke's Specialist Center",
              image: "https://images.unsplash.com/photo-1586773860418-d37222d8fce3",
              rating: "4.7",
              location: "High Street, North Wing",
              distance: "3.5 km",
              beds: 12,
            ),
          ],
        ),
      ),
    );
  }
}