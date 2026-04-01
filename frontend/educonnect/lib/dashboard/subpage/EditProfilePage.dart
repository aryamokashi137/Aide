import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class EditProfilePage extends StatefulWidget {
  final Map<String, dynamic> initialData;
  const EditProfilePage({super.key, required this.initialData});

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  final ApiService _apiService = ApiService();
  final _formKey = GlobalKey<FormState>();
  
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _bloodGroupController;
  late TextEditingController _emergency1Controller;
  late TextEditingController _emergency2Controller;
  late TextEditingController _instaController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final d = widget.initialData;
    _nameController = TextEditingController(text: d['full_name'] ?? '');
    _phoneController = TextEditingController(text: d['phone'] ?? '');
    _bloodGroupController = TextEditingController(text: d['blood_group'] ?? '');
    _emergency1Controller = TextEditingController(text: d['emergency_contact_1'] ?? '');
    _emergency2Controller = TextEditingController(text: d['emergency_contact_2'] ?? '');
    _instaController = TextEditingController(text: d['social_instagram'] ?? '');
    _linkedinController = TextEditingController(text: d['social_linkedin'] ?? '');
    _githubController = TextEditingController(text: d['social_github'] ?? '');
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    try {
      final updatedData = {
        'full_name': _nameController.text,
        'phone': _phoneController.text,
        'blood_group': _bloodGroupController.text,
        'emergency_contact_1': _emergency1Controller.text,
        'emergency_contact_2': _emergency2Controller.text,
        'social_instagram': _instaController.text,
        'social_linkedin': _linkedinController.text,
        'social_github': _githubController.text,
      };

      await _apiService.updateUserProfile(updatedData);
      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Profile updated successfully!"), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Update failed: $e"), backgroundColor: Colors.redAccent),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Edit Student Profile", style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          if (_isLoading)
            const Padding(padding: EdgeInsets.all(16), child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.deepPurple)))
          else
            TextButton(
              onPressed: _saveProfile,
              child: const Text("SAVE", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.deepPurple)),
            )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _sectionHeader("Personal Details"),
              _buildTextField("Full Name", _nameController, Icons.person_outline),
              _buildTextField("Phone Number", _phoneController, Icons.phone_outlined, keyboard: TextInputType.phone),
              _buildTextField("Blood Group", _bloodGroupController, Icons.bloodtype_outlined),

              const SizedBox(height: 25),
              _sectionHeader("Emergency Contacts"),
              _buildTextField("Primary Contact", _emergency1Controller, Icons.contact_emergency_outlined, keyboard: TextInputType.phone),
              _buildTextField("Secondary Contact", _emergency2Controller, Icons.contact_phone_outlined, keyboard: TextInputType.phone),

              const SizedBox(height: 25),
              _sectionHeader("Social Presence"),
              _buildTextField("Instagram Username", _instaController, Icons.camera_alt_outlined),
              _buildTextField("LinkedIn Profile", _linkedinController, Icons.work_outline),
              _buildTextField("GitHub Username", _githubController, Icons.code_outlined),
              
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _sectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 4),
      child: Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.deepPurple)),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, IconData icon, {TextInputType keyboard = TextInputType.text}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboard,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon, size: 20),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: isDark ? Colors.white.withOpacity(0.04) : Colors.grey.shade50,
        ),
        validator: (v) => (v == null || v.isEmpty) && label == "Full Name" ? "Full Name is required" : null,
      ),
    );
  }
}
