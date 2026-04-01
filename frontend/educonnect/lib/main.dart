import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'onboarding_page.dart';
import 'services/theme_provider.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => ThemeProvider(),
      child: const EduConnectApp(),
    ),
  );
}

class EduConnectApp extends StatelessWidget {
  const EduConnectApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'EduConnect',
      themeMode: themeProvider.themeMode,
      theme: ThemeData(
        brightness: Brightness.light,
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.deepPurple,
        useMaterial3: true,
      ),
      home: const OnboardingPage(),
    );
  }
}