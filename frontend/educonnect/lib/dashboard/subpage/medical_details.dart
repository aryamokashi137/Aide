import 'package:educonnect/models/review.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:flutter/material.dart';
import 'package:educonnect/widgets/review_dialog.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MedicalDetailsPage extends StatefulWidget {
  final int id;
  final String name;
  final String category;
  final String image;
  final String location;
  final String rating;
  final int availableBeds;
  final String emergencyContact;
  final String? phone;
  final String? website;

  const MedicalDetailsPage({
    super.key,
    required this.id,
    required this.name,
    required this.category,
    required this.image,
    required this.location,
    required this.rating,
    required this.availableBeds,
    required this.emergencyContact,
    this.phone,
    this.website,
  });

  @override
  State<MedicalDetailsPage> createState() => _MedicalDetailsPageState();
}

class _MedicalDetailsPageState extends State<MedicalDetailsPage> {
  final ApiService _apiService = ApiService();
  late Future<List<Review>> _reviewsFuture;

  @override
  void initState() {
    super.initState();
    _refreshReviews();
  }

  String get _backendType {
    final cat = widget.category.toLowerCase();
    if (cat.contains("doctor")) return "doctor";
    if (cat.contains("blood bank")) return "blood_bank";
    if (cat.contains("ambulance")) return "ambulance";
    return "hospital";
  }

  void _refreshReviews() {
    setState(() {
      _reviewsFuture = _apiService.getReviews(_backendType, widget.id);
    });
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _infoCard({required Widget child}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border.all(color: isDark ? Colors.white12 : Colors.grey.shade300),
        borderRadius: BorderRadius.circular(16),
      ),
      child: child,
    );
  }

  Widget _contactSection() {
    return _infoCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Contact Information", style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(children: [const Icon(Icons.emergency_outlined, size: 18, color: Colors.redAccent), const SizedBox(width: 10), Text(widget.emergencyContact)]),
          const SizedBox(height: 8),
          if (widget.phone != null) ...[
            Row(children: [const Icon(Icons.phone_outlined, size: 18, color: Colors.blue), const SizedBox(width: 10), Text(widget.phone!)]),
            const SizedBox(height: 8),
          ],
          if (widget.website != null) ...[
            Row(children: [const Icon(Icons.language_outlined, size: 18, color: Colors.blue), const SizedBox(width: 10), Text(widget.website!)]),
          ],
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        bottomNavigationBar: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: 4,
            ),
            child: const Text("Book Appointment / Visit", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ),
        body: Column(
          children: [
            /// HEADER IMAGE
            Stack(
              children: [
                Image.network(
                  widget.image,
                  height: 240, width: double.infinity, fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(height: 240, color: Colors.grey, child: const Icon(Icons.local_hospital_outlined, size: 60, color: Colors.white24)),
                ),
                Positioned(
                  top: 40, left: 16,
                  child: CircleAvatar(
                    backgroundColor: Colors.black45,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                ),
              ],
            ),

            /// CONTENT
            Expanded(
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.name, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            const Icon(Icons.star_rounded, color: Colors.orange, size: 24),
                            const SizedBox(width: 4),
                            Text(widget.rating, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                            const Spacer(),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                const Text("Available Beds", style: TextStyle(color: Colors.grey, fontSize: 11)),
                                Text(widget.availableBeds.toString(), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green)),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            const Icon(Icons.location_on_outlined, size: 18, color: Colors.grey),
                            const SizedBox(width: 6),
                            Expanded(child: Text(widget.location, style: const TextStyle(color: Colors.grey, fontSize: 13))),
                          ],
                        ),
                      ],
                    ),
                  ),

                  /// TABS
                  TabBar(
                    labelColor: Colors.redAccent,
                    unselectedLabelColor: Colors.grey,
                    indicatorColor: Colors.redAccent,
                    indicatorWeight: 3,
                    labelStyle: const TextStyle(fontWeight: FontWeight.bold),
                    tabs: const [Tab(text: "Overview"), Tab(text: "Services"), Tab(text: "Reviews")],
                  ),

                  Expanded(
                    child: TabBarView(
                      children: [
                        _overviewTab(),
                        _servicesTab(),
                        _reviewsTab(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _overviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle("About This Facility"),
          _infoCard(child: const Text("Providing compassionate and world-class healthcare with specialized treatment wings, advanced diagnostic labs, and 24/7 emergency support.", style: TextStyle(height: 1.6))),
          
          _sectionTitle("Working Hours"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: Icon(Icons.access_time), title: Text("Emergency / ICU"), trailing: Text("24/7", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold))),
              Divider(),
              ListTile(leading: Icon(Icons.calendar_month), title: Text("OPD Consultations"), trailing: Text("9 AM - 8 PM", style: TextStyle(fontWeight: FontWeight.bold))),
            ],
          )),

          _contactSection(),
        ],
      ),
    );
  }

  Widget _servicesTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle("Medical Specialities"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: Icon(Icons.favorite_outline, color: Colors.red), title: Text("Cardiology & Heart Surgery")),
              Divider(),
              ListTile(leading: Icon(Icons.psychology_outlined, color: Colors.blue), title: Text("Neurology")),
              Divider(),
              ListTile(leading: Icon(Icons.child_care_outlined, color: Colors.orange), title: Text("Pediatrics")),
              Divider(),
              ListTile(leading: Icon(Icons.biotech_outlined, color: Colors.purple), title: Text("Advanced Diagnostics")),
            ],
          )),

          _sectionTitle("Available Facilities"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: Icon(Icons.emergency), title: Text("24/7 Emergency & ICU")),
              Divider(),
              ListTile(leading: Icon(Icons.masks_outlined), title: Text("State-of-the-art Operation Theaters")),
              Divider(),
              ListTile(leading: Icon(Icons.medication_outlined), title: Text("Internal Pharmacy")),
            ],
          )),

          _contactSection(),
        ],
      ),
    );
  }

  Widget _reviewsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          ElevatedButton.icon(
            onPressed: () async {
              final prefs = await SharedPreferences.getInstance();
              final token = prefs.getString('access_token');
              if (token == null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Please Login to post a review!"), backgroundColor: Colors.redAccent)
                );
                return;
              }

              final res = await showDialog<Map<String, dynamic>>(
                context: context, builder: (_) => ReviewDialog(entityName: widget.name)
              );
              if (res != null) {
                try {
                  await _apiService.postReview(_backendType, widget.id, res['rating'], res['comment']);
                  _refreshReviews();
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Thank you for your feedback!")));
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
                }
              }
            },
            icon: const Icon(Icons.rate_review_outlined, color: Colors.redAccent),
            label: const Text("Write Your Review", style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent.withOpacity(0.1), elevation: 0, padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12)),
          ),
          const SizedBox(height: 24),
          FutureBuilder<List<Review>>(
            future: _reviewsFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
              if (snapshot.hasError) return Text("Error loading reviews: ${snapshot.error}");
              if (!snapshot.hasData || snapshot.data!.isEmpty) return const Text("No reviews found.");

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final r = snapshot.data![index];
                  return _reviewItem(r.userName, r.userName[0], Colors.redAccent, r.rating.toString(), r.content);
                },
              );
            },
          ),
          const SizedBox(height: 20),
          _contactSection(),
        ],
      ),
    );
  }

  Widget _reviewItem(String name, String ini, Color color, String score, String comment) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? Colors.white.withOpacity(0.04) : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: isDark ? Colors.white10 : Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(radius: 20, backgroundColor: color.withOpacity(0.1), foregroundColor: color, child: Text(ini, style: const TextStyle(fontWeight: FontWeight.bold))),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Row(children: [const Icon(Icons.star, color: Colors.orange, size: 14), const SizedBox(width: 4), Text(score, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.orange))]),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(comment, style: TextStyle(color: isDark ? Colors.grey : Colors.blueGrey, fontSize: 14, height: 1.5)),
        ],
      ),
    );
  }
}
