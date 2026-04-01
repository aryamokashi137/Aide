import 'package:educonnect/models/review.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:flutter/material.dart';
import 'package:educonnect/widgets/review_dialog.dart';
import 'package:shared_preferences/shared_preferences.dart';

class EducationDetailsPage extends StatefulWidget {
  final int id;
  final String name;
  final String category;
  final String image;
  final String location;
  final String fees;
  final String rating;

  const EducationDetailsPage({
    super.key,
    required this.id,
    required this.name,
    required this.category,
    required this.image,
    required this.location,
    required this.fees,
    required this.rating,
  });

  @override
  State<EducationDetailsPage> createState() => _EducationDetailsPageState();
}

class _EducationDetailsPageState extends State<EducationDetailsPage> {
  final ApiService _apiService = ApiService();
  late Future<List<Review>> _reviewsFuture;

  @override
  void initState() {
    super.initState();
    _refreshReviews();
  }

  String get _backendType {
    final cat = widget.category.toLowerCase();
    if (cat.contains("college")) return "college";
    if (cat.contains("school")) return "school";
    if (cat.contains("coaching")) return "coaching";
    if (cat.contains("mess")) return "mess";
    return "college";
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
        children: const [
          Text("Contact Admissions", style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 12),
          Row(children: [Icon(Icons.phone_outlined, size: 18, color: Colors.deepPurple), SizedBox(width: 10), Text("+91 9876543210")]),
          SizedBox(height: 8),
          Row(children: [Icon(Icons.email_outlined, size: 18, color: Colors.deepPurple), SizedBox(width: 10), Text("admissions@edu-connect.com")]),
          SizedBox(height: 8),
          Row(children: [Icon(Icons.language_outlined, size: 18, color: Colors.deepPurple), SizedBox(width: 10), Text("www.edu-connect.com")]),
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
              backgroundColor: Colors.deepPurple,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: 4,
              shadowColor: Colors.deepPurple.withOpacity(0.4),
            ),
            child: const Text("Apply For Admission", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
                  errorBuilder: (_, __, ___) => Container(height: 240, color: Colors.grey, child: const Icon(Icons.school, size: 60, color: Colors.white24)),
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
                            Text(widget.fees, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.deepPurple)),
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
                    labelColor: Colors.deepPurple,
                    unselectedLabelColor: Colors.grey,
                    indicatorColor: Colors.deepPurple,
                    indicatorWeight: 3,
                    labelStyle: const TextStyle(fontWeight: FontWeight.bold),
                    tabs: const [Tab(text: "Overview"), Tab(text: "Admission"), Tab(text: "Reviews")],
                  ),

                  Expanded(
                    child: TabBarView(
                      children: [
                        _overviewTab(),
                        _admissionTab(),
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
          _sectionTitle("About This Institution"),
          _infoCard(child: const Text("Experience world-class academics with modern labs, state-of-the-art infrastructure, and a focus on holistic student development.", style: TextStyle(height: 1.6))),
          
          _sectionTitle("Courses Offered"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: Icon(Icons.science_outlined), title: Text("Science & Engineering")),
              Divider(),
              ListTile(leading: Icon(Icons.business_outlined), title: Text("Business Management")),
              Divider(),
              ListTile(leading: Icon(Icons.palette_outlined), title: Text("Arts & Humanity")),
            ],
          )),

          _sectionTitle("Facilities"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: Icon(Icons.menu_book_outlined), title: Text("Multi-Floor Digital Library")),
              Divider(),
              ListTile(leading: Icon(Icons.computer_outlined), title: Text("IBM Certified Research Hub")),
              Divider(),
              ListTile(leading: Icon(Icons.sports_soccer), title: Text("Outdoor Sports Arena")),
            ],
          )),

          _contactSection(),
        ],
      ),
    );
  }

  Widget _admissionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle("Admission Schedule"),
          _infoCard(child: const Text("Applications for the 2026 academic batch are now open. Final enrollment date is 15th August.", style: TextStyle(height: 1.6))),

          _sectionTitle("Process Flow"),
          _infoCard(child: Column(
            children: const [
              ListTile(leading: CircleAvatar(child: Text("1"), radius: 12), title: Text("Online Registration")),
              ListTile(leading: CircleAvatar(child: Text("2"), radius: 12), title: Text("Aptitude Assessment")),
              ListTile(leading: CircleAvatar(child: Text("3"), radius: 12), title: Text("Panel Interview")),
              ListTile(leading: CircleAvatar(child: Text("4"), radius: 12), title: Text("Payment & Enrollment")),
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
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Feedback submitted successfully!")));
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
                }
              }
            },
            icon: const Icon(Icons.rate_review_outlined, color: Colors.deepPurple),
            label: const Text("Write Your Review", style: TextStyle(color: Colors.deepPurple, fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple.withOpacity(0.1), elevation: 0, padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12)),
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
                  return _reviewItem(r.userName, r.userName[0], Colors.deepPurple, r.rating.toString(), r.content);
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