import 'package:flutter/material.dart';
import 'login_page.dart';
// import 'hover_button.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final PageController _controller = PageController();
  int currentPage = 0;

  final List<Map<String, dynamic>> onboardingData = [
    {
      "color": Colors.blue,
      "icon": Icons.school_rounded,
      "title": "Find Top Educational Institutions",
      "subtitle":
          "Explore trusted schools, colleges, and universities near you with complete details and reviews.",
    },
    {
      "color": Colors.deepPurple,
      "icon": Icons.home_rounded,
      "title": "Discover Perfect PG & Stays",
      "subtitle":
          "Browse verified PGs and student stays with pricing, facilities, photos, and ratings.",
    },
    {
      "color": Colors.pink,
      "icon": Icons.local_hospital_rounded,
      "title": "Locate Nearby Medical Facilities",
      "subtitle":
          "Quickly access hospitals, clinics, blood banks, and emergency services whenever needed.",
    },
  ];

  void goToLogin() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginPage()),
    );
  }

  Widget buildIndicator(int index) {
    bool isActive = currentPage == index;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      width: isActive ? 26 : 8,
      height: 8,
      decoration: BoxDecoration(
        color: isActive ? Colors.deepPurple : Colors.deepPurple.shade100,
        borderRadius: BorderRadius.circular(20),
      ),
    );
  }

  Widget buildPage({
    required Color color,
    required IconData icon,
    required String title,
    required String subtitle,
    required bool isLast,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
      child: Column(
        children: [
          const SizedBox(height: 60),

          /// SKIP BUTTON
          Align(
            alignment: Alignment.topRight,
            child: TextButton(
              onPressed: goToLogin,
              child: const Text(
                "Skip",
                style: TextStyle(
                  color: Colors.deepPurple,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),

          const Spacer(),

          /// ANIMATED ICON CIRCLE
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.85, end: 1),
            duration: const Duration(milliseconds: 700),
            curve: Curves.easeOutBack,
            builder: (context, scale, child) {
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 190,
                  height: 190,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [
                        color.withValues(alpha: 0.75),
                        color,
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: color.withValues(alpha: 0.25),
                        blurRadius: 30,
                        spreadRadius: 5,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Icon(icon, color: Colors.white, size: 80),
                ),
              );
            },
          ),

          const SizedBox(height: 55),

          /// TITLE
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 400),
            child: Text(
              title,
              key: ValueKey(title),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
                height: 1.3,
              ),
            ),
          ),

          const SizedBox(height: 18),

          /// SUBTITLE
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 500),
            child: Text(
              subtitle,
              key: ValueKey(subtitle),
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 15.5,
                height: 1.7,
              ),
            ),
          ),

          const Spacer(),

          /// PAGE INDICATORS
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(
              onboardingData.length,
              (index) => buildIndicator(index),
            ),
          ),

          const SizedBox(height: 35),

          /// BUTTON
          SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: isLast
                ? goToLogin
                : () {
                    _controller.nextPage(
                      duration: const Duration(milliseconds: 450),
                      curve: Curves.easeInOut,
                    );
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
              elevation: 6,
              shadowColor: Colors.blue.withValues(alpha: 0.3),
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: Text(
              isLast ? "Get Started" : "Next",
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),

          const SizedBox(height: 30),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F6FF),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.deepPurple.shade50,
              Colors.white,
              Colors.blue.shade50.withValues(alpha: 0.35),
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: PageView.builder(
          controller: _controller,
          onPageChanged: (index) {
            setState(() {
              currentPage = index;
            });
          },
          itemCount: onboardingData.length,
          itemBuilder: (context, index) {
            final item = onboardingData[index];
            return buildPage(
              color: item["color"],
              icon: item["icon"],
              title: item["title"],
              subtitle: item["subtitle"],
              isLast: index == onboardingData.length - 1,
            );
          },
        ),
      ),
    );
  }
}