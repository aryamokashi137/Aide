import 'package:educonnect/models/pg.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:educonnect/services/location_service.dart';
import 'package:educonnect/widgets/filter_bottom_sheet.dart';
import 'package:educonnect/widgets/shimmer_card.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'subpage/stay_details.dart';

class StayPGPage extends StatefulWidget {
  const StayPGPage({super.key});

  @override
  State<StayPGPage> createState() => _StayPGPageState();
}

class _StayPGPageState extends State<StayPGPage> {
  final ApiService _apiService = ApiService();
  late Future<List<PG>> _pgsFuture;
  final TextEditingController _searchController = TextEditingController();

  Map<String, dynamic> _activeFilters = {
    'radius': 10.0,
    'type': null,
    'rating': null,
  };

  @override
  void initState() {
    super.initState();
    _refreshResults();
  }

  Future<void> _refreshResults() async {
    setState(() {
      _pgsFuture = _fetchPGs();
    });
  }

  Future<List<PG>> _fetchPGs() async {
    Position? pos;
    try {
      pos = await LocationService.getCurrentLocation();
    } catch (_) {}

    final queryParams = {
      if (_searchController.text.isNotEmpty) 'query': _searchController.text,
      if (pos != null) 'lat': pos.latitude,
      if (pos != null) 'lon': pos.longitude,
      'radius': _activeFilters['radius'],
      if (_activeFilters['type'] != null) 'gender': _activeFilters['type'],
      if (_activeFilters['rating'] != null) 'min_rating': _activeFilters['rating'].toString().replaceAll('+', ''),
    };

    return await _apiService.getPGs(filters: queryParams);
  }

  void _showFilterSheet() async {
    final result = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => FilterBottomSheet(
        currentRadius: _activeFilters['radius'],
        currentType: _activeFilters['type'],
        currentRating: _activeFilters['rating'],
        entityType: 'pg',
      ),
    );

    if (result != null) {
      setState(() {
        _activeFilters = result;
      });
      _refreshResults();
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Find Your Stay",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),

              /// Search & Filter Row
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        hintText: "Search PG & stays...",
                        prefixIcon: const Icon(Icons.search),
                        filled: true,
                        fillColor: Theme.of(context).cardColor,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      onSubmitted: (_) => _refreshResults(),
                    ),
                  ),
                  const SizedBox(width: 10),
                  GestureDetector(
                    onTap: _showFilterSheet,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 6)],
                      ),
                      child: const Icon(Icons.tune, color: Colors.deepPurple),
                    ),
                  )
                ],
              ),
              const SizedBox(height: 15),

              /// Active Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _filterChip("Radius: ${_activeFilters['radius'].toInt()}km", Icons.map),
                    if (_activeFilters['type'] != null) 
                      _filterChip(_activeFilters['type'], Icons.person_outline),
                    if (_activeFilters['rating'] != null) 
                      _filterChip(_activeFilters['rating'], Icons.star),
                  ],
                ),
              ),

              const SizedBox(height: 15),

              Expanded(
                child: FutureBuilder<List<PG>>(
                  future: _pgsFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return ShimmerList();
                    } else if (snapshot.hasError) {
                      return Center(child: Text('Error: ${snapshot.error}'));
                    } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                      return const Center(child: Text('No properties found matches your filters'));
                    }

                    final pgs = snapshot.data!;
                    return ListView.builder(
                      itemCount: pgs.length,
                      itemBuilder: (context, index) => _pgCard(context, pgs[index]),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _filterChip(String label, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.deepPurple.withOpacity(0.08),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.deepPurple.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 14, color: Colors.deepPurple),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.deepPurple)),
        ],
      ),
    );
  }

  Widget _pgCard(BuildContext context, PG pg) {
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => PGDetailsPage(pg: pg)),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 20),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 10)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              child: Image.network(
                pg.image ?? "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                height: 180,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  height: 180, width: double.infinity, 
                  color: isDark ? Colors.grey.shade900 : Colors.grey.shade200,
                  child: const Icon(Icons.home, size: 50, color: Colors.grey),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(child: Text(pg.name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold))),
                      Text("₹${pg.rent}/mo", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: isDark ? Colors.purpleAccent : Colors.purple)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.orange, size: 18),
                      const SizedBox(width: 4),
                      Text("${pg.rating}"),
                      const SizedBox(width: 15),
                      const Icon(Icons.location_on_outlined, size: 16, color: Colors.grey),
                      const SizedBox(width: 4),
                      Expanded(child: Text(pg.address, style: const TextStyle(color: Colors.grey, fontSize: 13), overflow: TextOverflow.ellipsis)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (pg.distance != null)
                   Text("📍 ${pg.distance!.toStringAsFixed(1)} km away", style: TextStyle(color: Colors.blue.shade300, fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}