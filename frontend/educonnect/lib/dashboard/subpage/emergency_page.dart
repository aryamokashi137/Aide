import 'package:flutter/material.dart';

class EmergencyPage extends StatelessWidget {
  const EmergencyPage({super.key});

  Widget emergencyCard(String number, String title, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.9),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: color.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4))],
        ),
        child: Column(
          children: [
            const Icon(Icons.call, color: Colors.white, size: 28),
            const SizedBox(height: 10),
            Text(number,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold)),
            Text(title, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  Widget contactCard(BuildContext context, String name, String relation, String phone) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 8)],
        border: Border.all(color: isDark ? Colors.white10 : Colors.transparent),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                   Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                   Text(relation, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
                ],
              ),
              const Icon(Icons.emergency_share, color: Colors.redAccent, size: 20),
            ],
          ),

          const SizedBox(height: 16),

          GestureDetector(
            onTap: () {},
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 14),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.redAccent, Colors.red]),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.phone, color: Colors.white, size: 18),
                    const SizedBox(width: 8),
                    Text("Call $phone", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
          )
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
        title: const Text("Emergency Contacts", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: isDark ? Colors.white : Colors.black,
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.add_circle_outline))
        ],
      ),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 24, 16, 12),
            child: Text("Quick Services", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
          ),

          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                emergencyCard("108", "Ambulance", Colors.redAccent),
                emergencyCard("100", "Police", Colors.blueAccent),
                emergencyCard("101", "Fire", Colors.orangeAccent),
              ],
            ),
          ),

          const Padding(
            padding: EdgeInsets.fromLTRB(16, 32, 16, 12),
            child: Text("Personal SOS Contacts", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
          ),

          contactCard(context, "Priya Sharma", "Mother", "+91 9876543230"),
          contactCard(context, "Amit Sharma", "Father", "+91 9876543231"),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}