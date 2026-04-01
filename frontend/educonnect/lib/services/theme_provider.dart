import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;
  final ApiService _apiService = ApiService();

  ThemeMode get themeMode => _themeMode;

  ThemeProvider() {
    _loadTheme();
  }

  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final isDark = prefs.getBool('isDarkMode');
    
    if (isDark != null) {
      _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
      notifyListeners();
    }

    // Also try to sync from backend if possible
    try {
      final userProfile = await _apiService.getUserProfile();
      final backendDark = userProfile['dark_mode'] ?? false;
      if (backendDark != isDark) {
        _themeMode = backendDark ? ThemeMode.dark : ThemeMode.light;
        await prefs.setBool('isDarkMode', backendDark);
        notifyListeners();
      }
    } catch (_) {
      // Ignore backend sync error on startup if offline/not logged in
    }
  }

  Future<void> toggleTheme(bool isDark) async {
    _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isDarkMode', isDark);

    // Sync to backend
    try {
      await _apiService.updateUserProfile({'dark_mode': isDark});
    } catch (e) {
      print("Error syncing theme to backend: $e");
    }
  }
}
