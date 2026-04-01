import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'signup_page.dart';
import 'forgot_password_page.dart';
import 'hover_button.dart';
import 'location.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  final ApiService _apiService = ApiService();
  bool _isLoading = false;

  void handleLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      try {
        await _apiService.login(emailController.text, passwordController.text);
        if (!mounted) return;
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => const LocationPage(),
          ),
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Login failed: ${e.toString()}')),
        );
      } finally {
        if (mounted) setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(height: 20),
                  Icon(Icons.school, size: 80, color: isDark ? Colors.blueAccent : Colors.blue),
                  const SizedBox(height: 20),
                  Text(
                    "Welcome Back",
                    style: TextStyle(
                      fontSize: 28, 
                      fontWeight: FontWeight.bold,
                      color: isDark ? Colors.white : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 30),

                  /// EMAIL
                  TextFormField(
                    controller: emailController,
                    decoration: InputDecoration(
                      hintText: "Email",
                      prefixIcon: const Icon(Icons.email),
                      filled: true,
                      fillColor: Theme.of(context).cardColor,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) return "Email is required";
                      if (!value.contains("@")) return "Enter valid email";
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  /// PASSWORD
                  TextFormField(
                    controller: passwordController,
                    obscureText: true,
                    decoration: InputDecoration(
                      hintText: "Password",
                      prefixIcon: const Icon(Icons.lock),
                      filled: true,
                      fillColor: Theme.of(context).cardColor,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) return "Password is required";
                      if (value.length < 6) return "Minimum 6 characters";
                      return null;
                    },
                  ),

                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const ForgotPasswordPage(),
                          ),
                        );
                      },
                      child: const Text("Forgot Password?"),
                    ),
                  ),

                  const SizedBox(height: 24),

                  _isLoading 
                    ? const CircularProgressIndicator()
                    : HoverButton(
                        text: "Login",
                        onPressed: handleLogin,
                      ),

                  const SizedBox(height: 16),

                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const SignupPage(),
                        ),
                      );
                    },
                    child: const Text("Don't have an account? Sign up"),
                  ),

                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}