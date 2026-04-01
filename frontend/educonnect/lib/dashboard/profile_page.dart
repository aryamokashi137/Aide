import 'package:educonnect/services/api_service.dart';
import 'package:flutter/material.dart';
import 'subpage/saved_page.dart';
import 'subpage/review_page.dart';
import 'subpage/emergency_page.dart';
import 'subpage/settings_page.dart';
import 'subpage/EditProfilePage.dart';
import 'subpage/visits_page.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final ApiService _apiService = ApiService();
  late Future<Map<String, dynamic>> _profileFuture;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _profileFuture = _apiService.getUserProfile();
    });
  }

  /// 🔁 Reusable Tile
  Widget menuTile({
    required BuildContext context,
    required IconData icon,
    required String title,
    String? count,
    required Widget page,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ListTile(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => page),
        );
      },
      leading: CircleAvatar(
        backgroundColor: isDark 
            ? Colors.deepPurple.withOpacity(0.2) 
            : Colors.deepPurple.withOpacity(0.1),
        child: Icon(icon, color: isDark ? Colors.deepPurpleAccent : Colors.deepPurple),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (count != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: isDark ? Colors.grey.shade800 : Colors.grey.shade200,
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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: FutureBuilder<Map<String, dynamic>>(
        future: _profileFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final user = snapshot.data!;
          return SingleChildScrollView(
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
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: isDark ? Colors.black26 : Colors.black12, 
                        blurRadius: 8
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 30,
                            backgroundColor: Colors.grey.shade300,
                            backgroundImage: NetworkImage(
                              user['profile_image'] ??
                                  "https://randomuser.me/api/portraits/men/32.jpg",
                            ),
                            onBackgroundImageError: (_, __) {},
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                user['full_name'] ?? 'Unknown User',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                user['email'] ?? '',
                                style: TextStyle(color: isDark ? Colors.grey.shade400 : Colors.grey.shade700),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.location_on,
                                      size: 16, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text(
                                    user['address'] ?? 'Earth',
                                    style: const TextStyle(color: Colors.grey),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 15),

                      /// EDIT BUTTON
                      GestureDetector(
                        onTap: () async {
                          final result = await Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => EditProfilePage(initialData: user)),
                          );
                          if (result == true) {
                            _refresh();
                          }
                        },
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.deepPurple.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.person_outline, color: isDark ? Colors.deepPurpleAccent : Colors.deepPurple),
                              const SizedBox(width: 8),
                              Text(
                                "Edit Profile",
                                style: TextStyle(
                                  color: isDark ? Colors.deepPurpleAccent : Colors.deepPurple,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                /// 📋 MENU
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
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
                        icon: Icons.calendar_month_outlined,
                        title: "My Visits",
                        page: MyVisitsPage(),
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

                /// 🚪 LOGOUT
                GestureDetector(
                  onTap: () {
                    // Handle Logout
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor,
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
                ),
                const SizedBox(height: 20),
              ],
            ),
          );
        },
      ),
    );
  }
}