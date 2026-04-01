import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/api_service.dart';

class MyVisitsPage extends StatefulWidget {
  const MyVisitsPage({super.key});

  @override
  State<MyVisitsPage> createState() => _MyVisitsPageState();
}

class _MyVisitsPageState extends State<MyVisitsPage> {
  final ApiService _apiService = ApiService();
  late Future<List<Map<String, dynamic>>> _visitsFuture;

  @override
  void initState() {
    super.initState();
    _visitsFuture = _apiService.getMyVisits();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("My Site Tours", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _visitsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
          if (snapshot.hasError) return Center(child: Text("Error: ${snapshot.error}"));
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.calendar_today_outlined, size: 80, color: Colors.grey.withOpacity(0.5)),
                  const SizedBox(height: 16),
                  const Text("No visits scheduled yet", style: TextStyle(color: Colors.grey, fontSize: 16)),
                ],
              ),
            );
          }

          final visits = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: visits.length,
            itemBuilder: (context, index) {
              final v = visits[index];
              final date = DateTime.parse(v['visit_date']);
              final status = v['status'] as String;

              return Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: isDark ? Colors.black26 : Colors.black12, blurRadius: 4)],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            v['entity_name'],
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        _statusChip(status),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.calendar_month, size: 16, color: Colors.deepPurple),
                        const SizedBox(width: 8),
                        Text(DateFormat('EEE, MMM d').format(date), style: const TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(width: 15),
                        const Icon(Icons.access_time, size: 16, color: Colors.deepPurple),
                        const SizedBox(width: 8),
                        Text(v['preferred_time'] ?? 'Anytime'),
                      ],
                    ),
                    if (v['message'] != null && v['message'].isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text(
                        "Note: ${v['message']}",
                        style: const TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
                      ),
                    ],
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }

  Widget _statusChip(String status) {
    Color color = Colors.blue;
    if (status == 'pending') color = Colors.orange;
    if (status == 'confirmed') color = Colors.green;
    if (status == 'cancelled') color = Colors.red;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(
        status.toUpperCase(),
        style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }
}
