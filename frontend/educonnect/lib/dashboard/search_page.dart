import 'package:educonnect/dashboard/subpage/EducationDetailsPage.dart';
import 'package:educonnect/dashboard/subpage/medical_details.dart';
import 'package:educonnect/dashboard/subpage/stay_details.dart';
import 'package:educonnect/models/pg.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:educonnect/widgets/shimmer_card.dart';
import 'package:flutter/material.dart';

class GlobalSearchPage extends StatefulWidget {
  const GlobalSearchPage({super.key});

  @override
  State<GlobalSearchPage> createState() => _GlobalSearchPageState();
}

class _GlobalSearchPageState extends State<GlobalSearchPage> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _results = [];
  bool _isLoading = false;

  Future<void> _performSearch(String q) async {
    if (q.isEmpty) {
      setState(() => _results = []);
      return;
    }
    setState(() => _isLoading = true);
    try {
      final results = await _apiService.globalSearch(q);
      setState(() => _results = results);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Search failed: $e")));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("Search Everything", style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
        backgroundColor: Colors.transparent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _searchController,
              autofocus: true,
              decoration: InputDecoration(
                hintText: "Search colleges, schools, PGs, hospitals...",
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(icon: const Icon(Icons.clear), onPressed: () { _searchController.clear(); _performSearch(""); }),
                filled: true,
                fillColor: Theme.of(context).cardColor,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
              ),
              onChanged: (v) {
                // Debounce would be nice, but simple search for now
                _performSearch(v);
              },
            ),
            const SizedBox(height: 20),
            Expanded(
              child: _isLoading 
                ? const ShimmerList(itemCount: 5)
                : _results.isEmpty 
                  ? _emptyState()
                  : ListView.builder(
                      itemCount: _results.length,
                      itemBuilder: (context, index) {
                        final item = _results[index];
                        return _searchResultCard(item);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _emptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search_off_outlined, size: 80, color: Colors.grey.withOpacity(0.3)),
          const SizedBox(height: 16),
          const Text("Try searching for something specific", style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _searchResultCard(Map<String, dynamic> item) {
    final type = item['type'] as String;
    final category = item['category'] as String;
    final name = item['name'] as String;
    final image = item['image'] as String?;
    final id = item['id'] as int;

    IconData categoryIcon = Icons.info_outline;
    Color categoryColor = Colors.grey;

    if (category == 'Education') { categoryIcon = Icons.school; categoryColor = Colors.blue; }
    else if (category == 'Stay') { categoryIcon = Icons.home; categoryColor = Colors.purple; }
    else if (category == 'Medical') { categoryIcon = Icons.local_hospital; categoryColor = Colors.red; }

    return ListTile(
      onTap: () => _navigateToDetails(item),
      contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      leading: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: image != null 
          ? Image.network(image, width: 50, height: 50, fit: BoxFit.cover, errorBuilder: (_,__,___)=> _placeholder(categoryColor))
          : _placeholder(categoryColor),
      ),
      title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
      subtitle: Row(
        children: [
          Icon(categoryIcon, size: 14, color: categoryColor),
          const SizedBox(width: 4),
          Text(category, style: TextStyle(color: categoryColor, fontSize: 12, fontWeight: FontWeight.bold)),
          const SizedBox(width: 8),
          Text("• $type", style: const TextStyle(color: Colors.grey, fontSize: 12)),
        ],
      ),
      trailing: const Icon(Icons.chevron_right, size: 20, color: Colors.grey),
    );
  }

  Widget _placeholder(Color color) {
    return Container(width: 50, height: 50, color: color.withOpacity(0.1), child: Icon(Icons.image, color: color.withOpacity(0.5)));
  }

  void _navigateToDetails(Map<String, dynamic> item) {
    final type = item['type'] as String;
    final id = item['id'] as int;

    if (categoryMapping(type) == 'education') {
         Navigator.push(context, MaterialPageRoute(builder: (_) => EducationDetailsPage(
           id: id, name: item['name'], category: type.toUpperCase(), image: item['image'] ?? "", location: "...", fees: "...", rating: "..."
         )));
    } else if (type == 'pg' || type == 'hostel') {
         // Need a PG object or fetch it
         // For now, simplified
         Navigator.push(context, MaterialPageRoute(builder: (_) => PGDetailsPage(pg: PG(id: id, name: item['name'], address: "...", rating: 0.0, rent: 0, image: item['image'], foodIncluded: false, gender: 'Any'))));
    } else if (type == 'hospital') {
         Navigator.push(context, MaterialPageRoute(builder: (_) => MedicalDetailsPage(id: id, name: item['name'])));
    }
  }

  String categoryMapping(String type) {
    if (['college', 'school', 'coaching', 'mess'].contains(type)) return 'education';
    return '';
  }
}
