import 'package:educonnect/models/pg.dart';
import 'package:educonnect/models/review.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:educonnect/widgets/review_dialog.dart';
import 'package:educonnect/widgets/scheduling_dialog.dart';
import 'package:flutter/material.dart';

class PGDetailsPage extends StatefulWidget {
  final PG pg;
  const PGDetailsPage({super.key, required this.pg});

  @override
  State<PGDetailsPage> createState() => _PGDetailsPageState();
}

class _PGDetailsPageState extends State<PGDetailsPage> {
  final ApiService _apiService = ApiService();
  late Future<List<Review>> _reviewsFuture;

  @override
  void initState() {
    super.initState();
    _refreshReviews();
  }

  void _refreshReviews() {
    setState(() {
      _reviewsFuture = _apiService.getReviews('pg', widget.pg.id);
    });
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 12),
      child: Text(
        title,
        style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
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
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.white10 : Colors.grey.shade100),
      ),
      child: child,
    );
  }

  @override
  Widget build(BuildContext context) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        bottomNavigationBar: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton.icon(
            icon: const Icon(Icons.calendar_month),
            label: const Text("Schedule Visit"),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              backgroundColor: Colors.purple,
              foregroundColor: Colors.white,
              textStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () async {
              final res = await showDialog<Map<String, dynamic>>(
                context: context, 
                builder: (_) => SchedulingDialog(entityName: widget.pg.name)
              );

              if (res != null) {
                try {
                  await _apiService.scheduleVisit(
                    entityType: 'pg',
                    entityId: widget.pg.id,
                    entityName: widget.pg.name,
                    visitDate: res['date'],
                    preferredTime: res['time'],
                    message: res['message'],
                  );
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Visit scheduled! Check your profile for details."), backgroundColor: Colors.green)
                    );
                  }
                } catch (e) {
                   if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text("Failed to schedule: $e"), backgroundColor: Colors.redAccent)
                    );
                  }
                }
              }
            },
          ),
        ),
        appBar: AppBar(
          elevation: 0,
          backgroundColor: Colors.transparent,
          foregroundColor: isDark ? Colors.white : Colors.black,
          title: const Text("PG Details", style: TextStyle(fontWeight: FontWeight.bold)),
        ),
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Image.network(
                widget.pg.image ?? "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                height: 250, width: double.infinity, fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(height: 250, color: Colors.grey),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(widget.pg.name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.star, color: Colors.orange, size: 18),
                        Text("${widget.pg.rating}", style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const TabBar(
                      labelColor: Colors.purple,
                      unselectedLabelColor: Colors.grey,
                      indicatorColor: Colors.purple,
                      tabs: [Tab(text: "Overview"), Tab(text: "Amenities"), Tab(text: "Reviews")],
                    ),
                    const SizedBox(height: 15),
                    SizedBox(
                      height: 500,
                      child: TabBarView(
                        children: [
                          _overviewTab(),
                          _amenitiesTab(),
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
      ),
    );
  }

  Widget _overviewTab() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle("Description"),
        _infoCard(child: Text(
          widget.pg.description ?? "Perfect for students with focus on safety and comfort. This property offers a vibrant community and modern living spaces designed for productivity.",
          style: const TextStyle(height: 1.5),
        )),
        _sectionTitle("Pricing"),
        _infoCard(child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("Rent: ₹${widget.pg.rent}/mo", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.purple)),
            Text(widget.pg.foodIncluded ? "Food Included" : "Food Not Included", style: TextStyle(color: widget.pg.foodIncluded ? Colors.green : Colors.grey, fontSize: 12)),
          ],
        )),
      ],
    );
  }

  Widget _amenitiesTab() {
    final List<String> items = widget.pg.facilities?.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList() ?? [];
    
    if (items.isEmpty) {
      return Column(
        children: const [
          ListTile(leading: Icon(Icons.wifi, color: Colors.blue), title: Text("Unlimited WiFi")),
          ListTile(leading: Icon(Icons.security, color: Colors.red), title: Text("CCTV & Security")),
          ListTile(leading: Icon(Icons.restaurant, color: Colors.orange), title: Text("Hygienic Food")),
        ],
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ListTile(
          leading: const Icon(Icons.check_circle_outline, color: Colors.green),
          title: Text(items[index]),
        );
      },
    );
  }

  Widget _reviewsTab() {
    return Column(
      children: [
        ElevatedButton.icon(
          onPressed: () async {
            final res = await showDialog<Map<String, dynamic>>(
              context: context, builder: (_) => ReviewDialog(entityName: widget.pg.name)
            );
            if (res != null) {
              try {
                await _apiService.postReview('pg', widget.pg.id, res['rating'], res['comment']);
                _refreshReviews();
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Review posted!")));
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
              }
            }
          },
          icon: const Icon(Icons.rate_review),
          label: const Text("Add Review"),
          style: ElevatedButton.styleFrom(backgroundColor: Colors.purple.withOpacity(0.1), elevation: 0),
        ),
        const SizedBox(height: 15),
        Expanded(
          child: FutureBuilder<List<Review>>(
            future: _reviewsFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
              if (snapshot.hasError) return Text("Error: ${snapshot.error}");
              if (!snapshot.hasData || snapshot.data!.isEmpty) return const Text("No reviews yet.");

              return ListView.builder(
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final r = snapshot.data![index];
                  return _reviewItem(r.userName, r.userName[0], Colors.purple, r.rating.toString(), r.content);
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _reviewItem(String name, String ini, Color color, String score, String comment) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? Colors.white10 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(radius: 16, backgroundColor: color, child: Text(ini, style: const TextStyle(color: Colors.white))),
              const SizedBox(width: 10),
              Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              const Spacer(),
              const Icon(Icons.star, color: Colors.orange, size: 14),
              Text(score, style: const TextStyle(fontSize: 12)),
            ],
          ),
          const SizedBox(height: 8),
          Text(comment, style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }
}
