import 'package:flutter/material.dart';
import 'subpage/saved_page.dart';
import 'subpage/review_page.dart';
import 'subpage/emergency_page.dart';
import 'subpage/settings_page.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  /// 🔁 Reusable Tile
  Widget menuTile({
    required BuildContext context,
    required IconData icon,
    required String title,
    String? count,
    required Widget page,
  }) {
    return ListTile(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => page),
        );
      },
      leading: CircleAvatar(
        backgroundColor: Colors.deepPurple.withOpacity(0.1),
        child: Icon(icon, color: Colors.deepPurple),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (count != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(count),
            ),
          const SizedBox(width: 6),
          const Icon(Icons.chevron_right, color: Colors.grey),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: SingleChildScrollView(
        child: Column(
          children: [
            /// 🔵 HEADER
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 50, 16, 20),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF5F2EEA), Color(0xFF7A4DFF)],
                ),
              ),
              child: const Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  "Profile",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            /// 👤 USER CARD
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              transform: Matrix4.translationValues(0, -30, 0),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [
                  BoxShadow(color: Colors.black12, blurRadius: 8),
                ],
              ),
              child: Column(
                children: [
                  Row(
                    children: const [
                      CircleAvatar(
                        radius: 30,
                        backgroundImage: NetworkImage(
                          "https://randomuser.me/api/portraits/men/32.jpg",
                        ),
                      ),
                      SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Rahul Sharma",
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text("rahul.sharma@email.com"),
                          SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(Icons.location_on,
                                  size: 16, color: Colors.grey),
                              SizedBox(width: 4),
                              Text("Bangalore, Karnataka"),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),

                  const SizedBox(height: 15),

                  /// EDIT BUTTON
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.deepPurple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.person_outline, color: Colors.deepPurple),
                        SizedBox(width: 8),
                        Text(
                          "Edit Profile",
                          style: TextStyle(
                            color: Colors.deepPurple,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            /// 📋 MENU
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  menuTile(
                    context: context,
                    icon: Icons.bookmark_border,
                    title: "Saved Listings",
                    count: "8",
                    page: const SavedListingsPage(),
                  ),

                  const Divider(height: 1),

                  menuTile(
                    context: context,
                    icon: Icons.star_border,
                    title: "My Reviews",
                    count: "5",
                    page: const ReviewsPage(),
                  ),

                  const Divider(height: 1),

                  menuTile(
                    context: context,
                    icon: Icons.phone_outlined,
                    title: "Emergency Contacts",
                    count: "2",
                    page: const EmergencyPage(),
                  ),

                  const Divider(height: 1),

                  menuTile(
                    context: context,
                    icon: Icons.settings,
                    title: "Settings",
                    page: const SettingsPage(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 15),

            /// 📅 MEMBER
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Column(
                children: [
                  Text("Member since", style: TextStyle(color: Colors.grey)),
                  SizedBox(height: 6),
                  Text(
                    "January 2024",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 15),

            /// 🚪 LOGOUT
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.logout, color: Colors.red),
                  SizedBox(width: 8),
                  Text(
                    "Logout",
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}