import 'package:flutter/material.dart';
import 'education_page.dart';
import 'medical_page.dart';
import 'stay_pg_page.dart';
import 'profile_page.dart';

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
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 244, 244, 247),
      extendBody: true,
      

      appBar: AppBar(
        title: const Text("Smart City"),
        backgroundColor: const Color.fromARGB(255, 254, 252, 252),
        foregroundColor: Colors.black,
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

      backgroundColor: Colors.white,
      selectedItemColor: Colors.blue,
      unselectedItemColor: Colors.grey,

      selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
      showUnselectedLabels: true,

      elevation: 10,

      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.school),
          label: "Education",
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.local_hospital),
          label: "Medical",
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: "Stay/PG",
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: "Profile",
        ),
      ],
    ),
    );
  }
}