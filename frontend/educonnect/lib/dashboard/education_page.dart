import 'package:educonnect/dashboard/subpage/EducationDetailsPage.dart';
import 'package:educonnect/models/college.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:educonnect/services/location_service.dart';
import 'package:educonnect/widgets/filter_bottom_sheet.dart';
import 'package:educonnect/widgets/shimmer_card.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

class EducationPage extends StatefulWidget {
  const EducationPage({super.key});

  @override
  State<EducationPage> createState() => _EducationPageState();
}

class _EducationPageState extends State<EducationPage> {
  final ApiService _apiService = ApiService();
  
  late Future<List<College>> _dataFuture;
  final TextEditingController _searchController = TextEditingController();
  
  String _activeTab = 'Colleges';

  Map<String, dynamic> _filters = {
    'radius': 10.0,
    'type': null,
    'rating': null,
    'sort_by': 'distance',
    'order': 'asc',
  };

  @override
  void initState() {
    super.initState();
    _refreshResults();
  }

  Future<void> _refreshResults() async {
    setState(() {
      _dataFuture = _fetchData(_activeTab.toLowerCase());
    });
  }

  Future<List<College>> _fetchData(String type) async {
    Position? pos;
    try {
      pos = await LocationService.getCurrentLocation();
    } catch (_) {}

    final queryParams = {
      if (_searchController.text.isNotEmpty) 'query': _searchController.text,
      if (pos != null) 'lat': pos.latitude,
      if (pos != null) 'lon': pos.longitude,
      'radius': _filters['radius'],
      'sort_by': _filters['sort_by'],
      'order': _filters['order'],
      if (_filters['rating'] != null) 'min_rating': _filters['rating'].toString().replaceAll('+', ''),
    };

    switch (type) {
      case 'schools': return await _apiService.getSchools(filters: queryParams);
      case 'coaching': return await _apiService.getCoaching(filters: queryParams);
      case 'mess': return await _apiService.getMess(filters: queryParams);
      default: return await _apiService.getColleges(filters: queryParams);
    }
  }

  void _showFilterSheet() async {
    final result = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => FilterBottomSheet(
        currentRadius: _filters['radius'],
        currentType: _filters['type'],
        currentRating: _filters['rating'],
        currentSortBy: _filters['sort_by'],
        currentOrder: _filters['order'],
        entityType: 'education',
      ),
    );

    if (result != null) {
      setState(() {
        _filters = result;
      });
      _refreshResults();
    }
  }

  Widget _categoryCard(String title, IconData icon, Color color) {
    bool isActive = _activeTab == title;
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          _activeTab = title;
        });
        _refreshResults();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 100,
        margin: const EdgeInsets.only(right: 12),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isActive 
              ? color.withOpacity(isDark ? 0.3 : 0.2) 
              : color.withOpacity(isDark ? 0.1 : 0.05),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isActive ? color : color.withOpacity(0.2),
            width: isActive ? 2 : 1,
          ),
          boxShadow: isActive ? [BoxShadow(color: color.withOpacity(0.2), blurRadius: 8)] : null,
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              title, 
              style: TextStyle(
                fontSize: 12, 
                fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
                color: isActive ? (isDark ? Colors.white : Colors.black) : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// SEARCH & FILTER
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: "Search in $_activeTab...",
                    prefixIcon: const Icon(Icons.search_outlined),
                    filled: true,
                    fillColor: Theme.of(context).cardColor,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(15),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onSubmitted: (_) => _refreshResults(),
                ),
              ),
              const SizedBox(width: 10),
              Container(
                decoration: BoxDecoration(
                  color: isDark ? Colors.white.withOpacity(0.05) : Colors.black.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: IconButton(
                  icon: const Icon(Icons.tune_outlined, color: Colors.deepPurple),
                  onPressed: _showFilterSheet,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),

          /// Active Sort Info
          Padding(
            padding: const EdgeInsets.only(left: 4),
            child: Row(
               children: [
                 const Icon(Icons.sort, color: Colors.grey, size: 14),
                 const SizedBox(width: 6),
                 Text(
                   "Sorted by ${_filters['sort_by']} (${_filters['order']})",
                   style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.bold),
                 ),
               ],
            ),
          ),

          const SizedBox(height: 15),
          
          /// QUICK CATEGORIES 
          const Text("Education Categories", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _categoryCard("Colleges", Icons.school_outlined, Colors.blue),
                _categoryCard("Schools", Icons.location_city_outlined, Colors.green),
                _categoryCard("Coaching", Icons.menu_book_outlined, Colors.orange),
                _categoryCard("Mess", Icons.restaurant_outlined, Colors.red),
              ],
            ),
          ),
          const SizedBox(height: 30),

          /// RESULT LIST
          Expanded(
            child: FutureBuilder<List<College>>(
              future: _dataFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return ShimmerList();
                } else if (snapshot.hasError) {
                  return _errorView(snapshot.error.toString());
                } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return _emptyView();
                }

                final items = snapshot.data!;
                return ListView.builder(
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return institutionCard(
                      context: context,
                      id: item.id,
                      name: item.name,
                      category: _activeTab.toUpperCase(),
                      image: item.image ?? _getDefaultImage(_activeTab.toLowerCase()),
                      location: item.address,
                      fees: "Price: ₹${item.fees}",
                      rating: "${item.rating} ${item.distance != null ? '(${item.distance!.toStringAsFixed(1)} km)' : ''}",
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  String _getDefaultImage(String type) {
    switch (type) {
      case 'schools': return "https://images.unsplash.com/photo-1546410531-bb4caa6b424d";
      case 'coaching': return "https://images.unsplash.com/photo-1524178232363-1fb2b075b655";
      case 'mess': return "https://images.unsplash.com/photo-1504674900247-0877df9cc836";
      default: return "https://images.unsplash.com/photo-1596495577886-d920f1fb7238";
    }
  }

  Widget _errorView(String err) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 50, color: Colors.red),
          const SizedBox(height: 10),
          Text('Error: $err'),
          TextButton(onPressed: _refreshResults, child: const Text("Retry"))
        ],
      ),
    );
  }

  Widget _emptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.search_off_outlined, size: 60, color: Colors.grey),
          const SizedBox(height: 10),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text('Nothing found with current filters', textAlign: TextAlign.center),
          ),
          TextButton(onPressed: _refreshResults, child: const Text("Refresh"))
        ],
      ),
    );
  }

  Widget institutionCard({
    required BuildContext context,
    required int id,
    required String name,
    required String category,
    required String image,
    required String location,
    required String fees,
    required String rating,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => EducationDetailsPage(
              id: id,
              name: name,
              category: category,
              image: image,
              location: location,
              fees: fees,
              rating: rating,
              description: item.description,
              streams: item.streamsAvailable,
              courses: item.coursesOffered,
            ),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 8)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              child: Image.network(
                image,
                height: 160, width: double.infinity, fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  height: 160, width: double.infinity, 
                  color: isDark ? Colors.grey.shade900 : Colors.grey.shade200,
                  child: const Icon(Icons.image_not_supported_outlined, size: 50, color: Colors.grey),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(child: Text(name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold))),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.star_outline, color: Colors.orange, size: 16),
                      const SizedBox(width: 4),
                      Text(rating, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                      const Spacer(),
                      Text(fees, style: TextStyle(fontWeight: FontWeight.bold, color: isDark ? Colors.blueAccent : Colors.blue.shade900)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, color: Colors.grey, size: 14),
                      const SizedBox(width: 4),
                      Expanded(child: Text(location, style: const TextStyle(color: Colors.grey, fontSize: 12), overflow: TextOverflow.ellipsis)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}