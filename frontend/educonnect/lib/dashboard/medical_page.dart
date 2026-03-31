import 'package:flutter/material.dart';

class MedicalPage extends StatelessWidget {
  const MedicalPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F6FA),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              /// 🔹 Title
              const Text(
                "Medical",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 4),

              /// 🔹 Location
              Row(
                children: const [
                  Icon(Icons.location_on_outlined,
                      size: 18, color: Colors.grey),
                  SizedBox(width: 4),
                  Text(
                    "Bangalore, Karnataka",
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              /// 🔹 Search Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: const [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 6,
                    ),
                  ],
                ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.search),
                    hintText: "Search hospitals...",
                    border: InputBorder.none,
                  ),
                ),
              ),

              const SizedBox(height: 20),

              /// 🔹 Blood Bank & Ambulance Buttons
              Row(
                children: [
                  _medicalChip(
                    icon: Icons.bloodtype_outlined,
                    label: "Blood Bank",
                    borderColor: Colors.red,
                  ),
                  const SizedBox(width: 12),
                  _medicalChip(
                    icon: Icons.local_hospital_outlined,
                    label: "Ambulance",
                    borderColor: Colors.blue,
                  ),
                ],
              ),

              const SizedBox(height: 25),

              /// 🔹 Hospitals Found
              const Text(
                "2 hospitals found",
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),

              const SizedBox(height: 16),

              /// 🔹 Hospital Card
              _medicalHospitalCard(),

              const SizedBox(height: 20),

              /// 🔹 Second Hospital (Duplicate for UI)
              _medicalHospitalCard(),
            ],
          ),
        ),
      ),
    );
  }

  /// 🔹 Reusable Button Widget
  static Widget _medicalChip({
    required IconData icon,
    required String label,
    required Color borderColor,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          border: Border.all(color: borderColor),
          borderRadius: BorderRadius.circular(30),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 18),
            const SizedBox(width: 8),
            Text(label),
          ],
        ),
      ),
    );
  }

  /// 🔹 Hospital Card Widget
  static Widget _medicalHospitalCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          /// 🔹 Image Section
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(20),
                ),
                child: Image.network(
                  "https://images.unsplash.com/photo-1586773860418-d37222d8fce3",
                  height: 180,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),

              /// 24/7 Badge
              Positioned(
                top: 12,
                left: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    "24/7 Emergency",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),

              /// Distance Badge
              Positioned(
                top: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    "1.2 km",
                    style: TextStyle(fontSize: 12),
                  ),
                ),
              ),
            ],
          ),

          /// 🔹 Details Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [

                const Text(
                  "Apollo Hospitals",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 6),

                Row(
                  children: const [
                    Icon(Icons.star,
                        color: Colors.orange, size: 18),
                    SizedBox(width: 4),
                    Text("4.7"),
                    SizedBox(width: 6),
                    Text("(892)",
                        style:
                            TextStyle(color: Colors.grey)),
                  ],
                ),

                const SizedBox(height: 8),

                Row(
                  children: const [
                    Icon(Icons.location_on_outlined,
                        size: 16, color: Colors.grey),
                    SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        "154 Bannerghatta Road, Bangalore",
                        style:
                            TextStyle(color: Colors.grey),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 10),

                Wrap(
                  spacing: 8,
                  children: [
                    _specialityChip("Cardiology"),
                    _specialityChip("Neurology"),
                    _specialityChip("Orthopedics"),
                    _specialityChip("+3 more"),
                  ],
                ),

                const Divider(height: 25),

                Row(
                  mainAxisAlignment:
                      MainAxisAlignment.spaceBetween,
                  children: const [
                    Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Text("Available Beds",
                            style: TextStyle(
                                color: Colors.grey)),
                        SizedBox(height: 4),
                        Text("45/250",
                            style: TextStyle(
                                fontWeight:
                                    FontWeight.bold)),
                      ],
                    ),
                    Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Text("ICU Beds",
                            style: TextStyle(
                                color: Colors.grey)),
                        SizedBox(height: 4),
                        Text("8/30",
                            style: TextStyle(
                                fontWeight:
                                    FontWeight.bold)),
                      ],
                    ),
                    Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.end,
                      children: [
                        Text("Consultation",
                            style: TextStyle(
                                color: Colors.grey)),
                        SizedBox(height: 4),
                        Text("₹500 - ₹2,000",
                            style: TextStyle(
                                fontWeight:
                                    FontWeight.bold)),
                      ],
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

  /// 🔹 Speciality Chip
  static Widget _specialityChip(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F3F6),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        text,
        style: const TextStyle(fontSize: 12),
      ),
    );
  }
}