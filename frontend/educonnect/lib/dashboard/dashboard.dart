import 'package:flutter/material.dart';
import 'education_page.dart';
import 'medical_page.dart';
import 'stay_pg_page.dart';
import 'profile_page.dart';
import 'search_page.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int currentIndex = 0;

  final List<Widget> pages = const [
    EducationPage(),
    MedicalPage(),
    StayPGPage(),
    GlobalSearchPage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    // Determine theme brightness
    final bool isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      extendBody: true,
      
      appBar: AppBar(
        title: const Text("EduCare Connect"),
        elevation: 0,
      ),

      body: pages[currentIndex],

      bottomNavigationBar: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: (index) {
          setState(() {
            currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        backgroundColor: Theme.of(context).cardColor,
        selectedItemColor: isDark ? Colors.blueAccent : Colors.blue,
        unselectedItemColor: isDark ? Colors.grey.shade500 : Colors.grey,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
        showUnselectedLabels: true,
        elevation: 10,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.school, size: 22),
            label: "Education",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_hospital, size: 22),
            label: "Medical",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.home, size: 22),
            label: "Stay/PG",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search, size: 22),
            label: "Search",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person, size: 22),
            label: "Profile",
          ),
        ],
      ),
    );
  }
}