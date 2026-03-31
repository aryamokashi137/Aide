import 'package:flutter/material.dart';
import 'onboarding_page.dart';

void main() {
  runApp(const EduConnectApp());
}

class EduConnectApp extends StatelessWidget {
  const EduConnectApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'EduConnect',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const OnboardingPage(),
    );
  }
}