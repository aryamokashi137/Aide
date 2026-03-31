import 'package:flutter/material.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool notifications = true;
  bool location = true;
  bool darkMode = false;

  Widget settingTile({
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
  }) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: Colors.deepPurple.withOpacity(0.1),
        child: Icon(icon, color: Colors.deepPurple),
      ),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: trailing,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(title: const Text("Settings")),
      body: ListView(
        children: [

          /// PREFERENCES
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text("PREFERENCES",
                style: TextStyle(color: Colors.grey)),
          ),

          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14)),
            child: Column(
              children: [

                settingTile(
                  icon: Icons.notifications,
                  title: "Notifications",
                  subtitle: "Receive alerts",
                  trailing: Switch(
                    value: notifications,
                    onChanged: (v) => setState(() => notifications = v),
                  ),
                ),

                settingTile(
                  icon: Icons.location_on,
                  title: "Location Access",
                  subtitle: "Allow access",
                  trailing: Switch(
                    value: location,
                    onChanged: (v) => setState(() => location = v),
                  ),
                ),

                settingTile(
                  icon: Icons.dark_mode,
                  title: "Dark Mode",
                  subtitle: "Switch theme",
                  trailing: Switch(
                    value: darkMode,
                    onChanged: (v) => setState(() => darkMode = v),
                  ),
                ),

                settingTile(
                  icon: Icons.language,
                  title: "Language",
                  subtitle: "English",
                  trailing: const Icon(Icons.chevron_right),
                ),
              ],
            ),
          ),

          /// SECURITY
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text("SECURITY",
                style: TextStyle(color: Colors.grey)),
          ),

          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14)),
            child: Column(
              children: const [
                ListTile(
                  leading: Icon(Icons.lock),
                  title: Text("Change Password"),
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.privacy_tip),
                  title: Text("Privacy Policy"),
                ),
              ],
            ),
          ),

          /// SUPPORT
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text("SUPPORT",
                style: TextStyle(color: Colors.grey)),
          ),

          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14)),
            child: const ListTile(
              leading: Icon(Icons.help_outline),
              title: Text("Help & Support"),
            ),
          ),

          const SizedBox(height: 20),

          const Center(child: Text("Version 1.0.0")),
        ],
      ),
    );
  }
}