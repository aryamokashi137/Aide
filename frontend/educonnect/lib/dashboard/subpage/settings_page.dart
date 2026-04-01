import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../services/theme_provider.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final ApiService _apiService = ApiService();
  bool location = true;
  String language = "English";
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final data = await _apiService.getUserProfile();
      if (mounted) {
        setState(() {
          location = data['location_access'] ?? true;
          language = data['preferred_language'] ?? "English";
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error loading settings: $e")),
        );
        setState(() => isLoading = false);
      }
    }
  }

  Future<void> _updateSetting(String key, dynamic value) async {
    try {
      await _apiService.updateUserProfile({key: value});
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error saving setting: $e")),
        );
      }
    }
  }

  Widget settingTile({
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: isDark 
            ? Colors.deepPurple.withOpacity(0.2) 
            : Colors.deepPurple.withOpacity(0.1),
        child: Icon(icon, color: isDark ? Colors.deepPurpleAccent : Colors.deepPurple),
      ),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: trailing,
    );
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.themeMode == ThemeMode.dark;

    return Scaffold(
      backgroundColor: isDark ? Colors.black : Colors.grey.shade100,
      appBar: AppBar(title: const Text("Settings")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                /// PREFERENCES
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text("PREFERENCES", style: TextStyle(color: Colors.grey)),
                ),

                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                      color: isDark ? Colors.grey.shade900 : Colors.white, 
                      borderRadius: BorderRadius.circular(14)),
                  child: Column(
                    children: [
                      settingTile(
                        icon: Icons.location_on,
                        title: "Location Access",
                        subtitle: "Allow access for nearby search",
                        trailing: Switch(
                          value: location,
                          onChanged: (v) {
                            setState(() => location = v);
                            _updateSetting('location_access', v);
                          },
                        ),
                      ),

                      const Divider(height: 1, indent: 70),

                      settingTile(
                        icon: Icons.dark_mode,
                        title: "Dark Mode",
                        subtitle: "Switch theme",
                        trailing: Switch(
                          value: isDark,
                          onChanged: (v) {
                            themeProvider.toggleTheme(v);
                          },
                        ),
                      ),

                      const Divider(height: 1, indent: 70),

                      settingTile(
                        icon: Icons.language,
                        title: "Language",
                        subtitle: language,
                        trailing: const Icon(Icons.chevron_right),
                      ),
                    ],
                  ),
                ),

                /// SECURITY
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text("SECURITY", style: TextStyle(color: Colors.grey)),
                ),

                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                      color: isDark ? Colors.grey.shade900 : Colors.white, 
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

                const SizedBox(height: 20),
                const Center(child: Text("Version 1.2.0")),
              ],
            ),
    );
  }
}