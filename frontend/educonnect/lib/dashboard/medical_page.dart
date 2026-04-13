import 'package:educonnect/models/hospital.dart';
import 'package:educonnect/services/api_service.dart';
import 'package:educonnect/services/location_service.dart';
import 'package:educonnect/widgets/shimmer_card.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'subpage/medical_details.dart';

class MedicalPage extends StatefulWidget {
  const MedicalPage({super.key});

  @override
  State<MedicalPage> createState() => _MedicalPageState();
}

class _MedicalPageState extends State<MedicalPage> {
  final ApiService _apiService = ApiService();
  late Future<List<Hospital>> _dataFuture;
  String _activeTab = 'Hospitals';

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _dataFuture = _fetchData();
    });
  }

  Future<List<Hospital>> _fetchData() async {
    Position? pos;
    try {
      pos = await LocationService.getCurrentLocation();
    } catch (_) {}

    final filters = {
      if (pos != null) 'lat': pos.latitude,
      if (pos != null) 'lon': pos.longitude,
      'radius': 15.0,
    };

    switch (_activeTab) {
      case 'Doctors': return await _apiService.getDoctors(filters: filters);
      case 'Blood Bank': return await _apiService.getBloodBanks(filters: filters);
      case 'Ambulance': return await _apiService.getAmbulances(filters: filters);
      default: return await _apiService.getHospitals(filters: filters);
    }
  }

  Widget _serviceCategory(String title, IconData icon, Color color) {
    bool isActive = _activeTab == title;
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: () {
        setState(() => _activeTab = title);
        _refresh();
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
          border: Border.all(color: isActive ? color : color.withOpacity(0.3), width: isActive ? 2 : 1),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              title, 
              style: TextStyle(
                fontSize: 12, 
                fontWeight: isActive ? FontWeight.bold : FontWeight.normal, 
                color: isDark ? Colors.white : Colors.black87
              )
            ),
          ],
        ),
      ),
    );
  }

  Widget _hospitalCard(Hospital h) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => MedicalDetailsPage(
              id: h.id,
              name: h.name,
              category: h.category,
              image: h.image ?? "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d",
              location: h.address,
              rating: h.rating.toString(),
              availableBeds: h.availableBeds,
              emergencyContact: h.emergencyContact,
              phone: h.phoneNumber,
              website: h.website,
            ),
          ),
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
            Stack(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  child: Image.network(
                    h.image ?? "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d",
                    height: 180, width: double.infinity, fit: BoxFit.cover,
                    errorBuilder: (_,__,___) => Container(height: 180, color: Colors.grey.shade900, child: const Icon(Icons.broken_image_outlined)),
                  ),
                ),
                if (h.distance != null)
                  Positioned(
                    top: 12, right: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(color: isDark ? Colors.black87 : Colors.white, borderRadius: BorderRadius.circular(20)),
                      child: Text("${h.distance!.toStringAsFixed(1)} km", style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    ),
                  ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(h.name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.star_outline, color: Colors.orange, size: 18),
                      const SizedBox(width: 4),
                      Text(h.rating.toString(), style: const TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(width: 10),
                      const Icon(Icons.location_on_outlined, color: Colors.grey, size: 16),
                      const SizedBox(width: 4),
                      Expanded(child: Text(h.address, style: const TextStyle(color: Colors.grey, fontSize: 13), overflow: TextOverflow.ellipsis)),
                    ],
                  ),
                  const SizedBox(height: 15),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text("Available Beds", style: TextStyle(color: Colors.grey, fontSize: 12)),
                          Text(h.availableBeds.toString(), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.green)),
                        ],
                      ),
                      ElevatedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.call_outlined, size: 16),
                        label: const Text("Emergency"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red.withOpacity(0.1),
                          foregroundColor: Colors.red,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))
                        ),
                      ),
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("Medical Services", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black,
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refresh(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              /// QUICK SERVICES
              const Text("Quick Services", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _serviceCategory("Hospitals", Icons.local_hospital_outlined, Colors.red),
                    _serviceCategory("Doctors", Icons.person_search_outlined, Colors.blue),
                    _serviceCategory("Blood Bank", Icons.bloodtype_outlined, Colors.redAccent),
                    _serviceCategory("Ambulance", Icons.airport_shuttle_outlined, Colors.orange),
                  ],
                ),
              ),
      
              const SizedBox(height: 30),
      
              /// LIST
              Text("Nearby $_activeTab", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              
              FutureBuilder<List<Hospital>>(
                future: _dataFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) return const ShimmerList();
                  if (snapshot.hasError) return Center(child: Text("Error loading data: ${snapshot.error}"));
                  if (!snapshot.hasData || snapshot.data!.isEmpty) return const Center(child: Text("No medical facilities found"));
                  
                  return ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: snapshot.data!.length,
                    itemBuilder: (context, index) => _hospitalCard(snapshot.data![index]),
                  );
                }
              ),
            ],
          ),
        ),
      ),
    );
  }
}