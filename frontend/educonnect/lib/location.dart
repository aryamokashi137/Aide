import 'package:flutter/material.dart';
import 'dashboard/dashboard.dart';

class LocationPage extends StatelessWidget {
  const LocationPage({super.key});

  @override
  Widget build(BuildContext context) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            /// Top Icon Circle
            Container(
              height: 110,
              width: 110,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: isDark 
                    ? [const Color(0xFF8C6DFF), const Color(0xFF6C4DFF)]
                    : [const Color(0xFF6C4DFF), const Color(0xFF4A34E0)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: isDark ? Colors.blueAccent.withOpacity(0.2) : Colors.black12,
                    blurRadius: 20,
                    spreadRadius: 2,
                  )
                ]
              ),
              child: const Icon(
                Icons.location_on_outlined,
                color: Colors.white,
                size: 50,
              ),
            ),

            const SizedBox(height: 40),

            /// Title
            Text(
              "Enable Location Access",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.white : Colors.black87,
              ),
            ),

            const SizedBox(height: 20),

            /// Description
            Text(
              "We need your location to show nearby educational "
              "institutions, medical facilities, and PG accommodations",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                color: isDark ? Colors.grey.shade400 : Colors.black54,
                height: 1.5,
              ),
            ),

            const SizedBox(height: 40),

            /// Allow Location Button (Gradient)
            SizedBox(
              width: double.infinity,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(14),
                  gradient: LinearGradient(
                    colors: isDark 
                      ? [const Color(0xFF8C6DFF), const Color(0xFF6C4DFF)]
                      : [const Color(0xFF6C4DFF), const Color(0xFF4A34E0)],
                  ),
                  boxShadow: [
                    if (!isDark) const BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))
                  ]
                ),
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const DashboardPage(),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: const Text(
                    "Allow Location Access",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 20),

            /// Skip Button
            TextButton(
              onPressed: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const DashboardPage(),
                  ),
                );
              },
              child: Text(
                "Skip for Now",
                style: TextStyle(
                  fontSize: 16,
                  color: isDark ? Colors.grey.shade300 : Colors.black87,
                ),
              ),
            ),

            const SizedBox(height: 30),

            /// Privacy Text
            Text(
              "Your location data is only used to provide relevant results\n"
              "and is never shared with third parties",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: isDark ? Colors.grey.shade600 : Colors.black45,
              ),
            ),
          ],
        ),
      ),
    );
  }
}