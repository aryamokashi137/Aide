import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/college.dart';
import '../models/hospital.dart';
import '../models/pg.dart';
import '../models/review.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';

  // Helper to get the token for every request
  Future<Map<String, String>> _getHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Generic helper to build a URL with any query parameters
  String _buildUrl(String path, Map<String, dynamic>? queryParams) {
    String url = '$baseUrl$path/'; // All paths end with /
    if (queryParams != null && queryParams.isNotEmpty) {
      List<String> parts = [];
      queryParams.forEach((key, value) {
        if (value != null) {
          parts.add('$key=${Uri.encodeComponent(value.toString())}');
        }
      });
      if (parts.isNotEmpty) {
        url += '?' + parts.join('&');
      }
    }
    return url;
  }

  // --- Education Module ---
  Future<List<College>> getColleges({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/education/colleges', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => College.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load colleges (Status: ${response.statusCode})');
    }
  }

  Future<List<College>> getSchools({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/education/schools', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => College.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load schools');
    }
  }

  Future<List<College>> getCoaching({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/education/coaching', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => College.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load coaching');
    }
  }

  Future<List<College>> getMess({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/education/mess', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => College.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load mess');
    }
  }

  // --- Medical Module ---
  Future<List<Hospital>> getHospitals({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/medical/hospitals', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Hospital.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load hospitals (Status: ${response.statusCode})');
    }
  }

  Future<List<Hospital>> getDoctors({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/medical/doctors', filters);
    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Hospital.fromJson(item)).toList();
    }
    throw Exception('Failed to load doctors');
  }

  Future<List<Hospital>> getBloodBanks({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/medical/blood-banks', filters);
    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Hospital.fromJson(item)).toList();
    }
    throw Exception('Failed to load blood banks');
  }

  Future<List<Hospital>> getAmbulances({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/medical/ambulances', filters);
    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Hospital.fromJson(item)).toList();
    }
    throw Exception('Failed to load ambulances');
  }

  // --- Stay Module ---
  Future<List<PG>> getPGs({Map<String, dynamic>? filters}) async {
    final headers = await _getHeaders();
    final url = _buildUrl('/stay/pgs', filters);
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => PG.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load PGs (Status: ${response.statusCode})');
    }
  }

  // --- Auth Module ---
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {
        'username': email,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', data['access_token']);
      return data;
    } else {
      throw Exception('Login failed');
    }
  }

  Future<void> register(String name, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'full_name': name,
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode != 201) {
      final data = json.decode(response.body);
      throw Exception(data['detail'] ?? 'Registration failed');
    }
  }

  Future<void> forgotPassword(String email) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/forgot-password'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'email': email}),
    );

    if (response.statusCode != 200) {
      final data = json.decode(response.body);
      throw Exception(data['detail'] ?? 'Failed to send reset code');
    }
  }

  Future<void> resetPassword(String email, String otp, String newPassword) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/reset-password'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'token': otp,
        'new_password': newPassword,
      }),
    );

    if (response.statusCode != 200) {
      final data = json.decode(response.body);
      throw Exception(data['detail'] ?? 'Password reset failed');
    }
  }

  Future<Map<String, dynamic>> getUserProfile() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/profile/profile/me'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load profile (Status: ${response.statusCode})');
    }
  }

  Future<Map<String, dynamic>> updateUserProfile(Map<String, dynamic> data) async {
    final headers = await _getHeaders();
    final response = await http.put(
      Uri.parse('$baseUrl/profile/profile/me'),
      headers: headers,
      body: json.encode(data),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to update profile (Status: ${response.statusCode})');
    }
  }

  // --- Reviews Module ---
  Future<List<Review>> getReviews(String targetType, int targetId) async {
    final headers = await _getHeaders();
    final url = '$baseUrl/reviews/$targetType/$targetId';
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Review.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load reviews');
    }
  }

  Future<void> postReview(String targetType, int targetId, int rating, String content) async {
    final headers = await _getHeaders();
    final url = '$baseUrl/reviews/?target_type=$targetType&target_id=$targetId';
    
    final response = await http.post(
      Uri.parse(url),
      headers: headers,
      body: json.encode({
        'content': content,
        'rating': rating,
      }),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
       final msg = json.decode(response.body)['detail'] ?? 'Unknown error';
       throw Exception('Failed to post review: $msg (Status: ${response.statusCode})');
    }
  }

  Future<List<Review>> getMyReviews() async {
    final headers = await _getHeaders();
    final url = '$baseUrl/reviews/me';
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      return body.map((item) => Review.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load your reviews');
    }
  }
  // --- Visits Module ---
  Future<void> scheduleVisit({
    required String entityType,
    required int entityId,
    required String entityName,
    required DateTime visitDate,
    String? preferredTime,
    String? message,
  }) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/visits/'),
      headers: headers,
      body: json.encode({
        'entity_type': entityType,
        'entity_id': entityId,
        'entity_name': entityName,
        'visit_date': visitDate.toIso8601String(),
        'preferred_time': preferredTime,
        'message': message,
      }),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to schedule visit: ${response.statusCode}');
    }
  }

  Future<List<Map<String, dynamic>>> getMyVisits() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/visits/me'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return List<Map<String, dynamic>>.from(data);
    } else {
      throw Exception('Failed to load visits');
    }
  }

  Future<List<Map<String, dynamic>>> globalSearch(String query) async {
    final headers = await _getHeaders();
    final url = '$baseUrl/search/?query=${Uri.encodeComponent(query)}';
    final response = await http.get(Uri.parse(url), headers: headers);

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return List<Map<String, dynamic>>.from(data);
    } else {
      throw Exception('Failed to perform search');
    }
  }
}
