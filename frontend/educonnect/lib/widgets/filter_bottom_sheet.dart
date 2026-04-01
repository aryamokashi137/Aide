import 'package:flutter/material.dart';

class FilterBottomSheet extends StatefulWidget {
  final double currentRadius;
  final String? currentType;
  final String? currentRating;
  final String? currentSortBy;
  final String? currentOrder;
  final String entityType; // 'education', 'pg', 'hospital'

  const FilterBottomSheet({
    super.key,
    required this.currentRadius,
    this.currentType,
    this.currentRating,
    this.currentSortBy,
    this.currentOrder,
    required this.entityType,
  });

  @override
  State<FilterBottomSheet> createState() => _FilterBottomSheetState();
}

class _FilterBottomSheetState extends State<FilterBottomSheet> {
  late double _radius;
  String? _selectedType;
  String? _selectedRating;
  String _selectedSortBy = "name";
  String _selectedOrder = "asc";

  @override
  void initState() {
    super.initState();
    _radius = widget.currentRadius;
    _selectedType = widget.currentType;
    _selectedRating = widget.currentRating;
    _selectedSortBy = widget.currentSortBy ?? "name";
    _selectedOrder = widget.currentOrder ?? "asc";
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 16),
      child: Text(
        title,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 30),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          /// Handle Bar
          Center(
            child: Container(
              width: 40, height: 4,
              decoration: BoxDecoration(color: Colors.grey.shade400, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          const SizedBox(height: 15),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text("Filter & Sort", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              TextButton(
                onPressed: () {
                  setState(() {
                    _radius = 10.0;
                    _selectedType = null;
                    _selectedRating = null;
                    _selectedSortBy = "name";
                    _selectedOrder = "asc";
                  });
                },
                child: const Text("Reset", style: TextStyle(color: Colors.red)),
              )
            ],
          ),

          const Divider(),

          /// RADIUS
          _sectionTitle("Search Radius (${_radius.toInt()} km)"),
          Slider(
            value: _radius,
            min: 1, max: 100,
            divisions: 99,
            activeColor: Colors.deepPurple,
            onChanged: (v) => setState(() => _radius = v),
          ),

          /// SORT BY
          _sectionTitle("Sort Results By"),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _choiceChip("Name", "name", _selectedSortBy, (v) => setState(() => _selectedSortBy = v)),
                _choiceChip("Rating", "rating", _selectedSortBy, (v) => setState(() => _selectedSortBy = v)),
                _choiceChip("Distance", "distance", _selectedSortBy, (v) => setState(() => _selectedSortBy = v)),
              ],
            ),
          ),

          /// ORDER
          _sectionTitle("Order"),
          Row(
            children: [
              _choiceChip("Ascending", "asc", _selectedOrder, (v) => setState(() => _selectedOrder = v)),
              const SizedBox(width: 10),
              _choiceChip("Descending", "desc", _selectedOrder, (v) => setState(() => _selectedOrder = v)),
            ],
          ),

          /// RATING
          _sectionTitle("Minimum Rating"),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: ["Any", "3.0+", "4.0+", "4.5+"].map((rating) {
              final isSelected = (_selectedRating ?? "Any") == rating;
              return GestureDetector(
                onTap: () => setState(() => _selectedRating = rating == "Any" ? null : rating),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.deepPurple : Colors.transparent,
                    border: Border.all(color: isSelected ? Colors.deepPurple : Colors.grey.withOpacity(0.5)),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: Text(
                    rating,
                    style: TextStyle(color: isSelected ? Colors.white : (isDark ? Colors.white70 : Colors.black87), fontWeight: isSelected ? FontWeight.bold : FontWeight.normal),
                  ),
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: 35),

          /// APPLY BUTTON
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.pop(context, {
                  'radius': _radius,
                  'type': _selectedType,
                  'rating': _selectedRating,
                  'sort_by': _selectedSortBy,
                  'order': _selectedOrder,
                });
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 0,
              ),
              child: const Text("Apply Filters", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _choiceChip(String label, String value, String selectedValue, Function(String) onSelected) {
    bool isSelected = value == selectedValue;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (v) => onSelected(value),
        selectedColor: Colors.deepPurple,
        labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.grey.shade700, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal),
        backgroundColor: Colors.grey.shade200,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide.none),
      ),
    );
  }
}
