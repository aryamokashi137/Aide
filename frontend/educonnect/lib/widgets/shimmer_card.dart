import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

class ShimmerCard extends StatelessWidget {
  final double height;
  final double width;
  final BorderRadius? borderRadius;

  const ShimmerCard({
    super.key, 
    required this.height, 
    this.width = double.infinity, 
    this.borderRadius
  });

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Shimmer.fromColors(
      baseColor: isDark ? Colors.grey.shade900 : Colors.grey.shade300,
      highlightColor: isDark ? Colors.grey.shade800 : Colors.grey.shade100,
      child: Container(
        height: height,
        width: width,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: borderRadius ?? BorderRadius.circular(16),
        ),
      ),
    );
  }
}

class ShimmerList extends StatelessWidget {
  final int itemCount;
  const ShimmerList({super.key, this.itemCount = 5});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: itemCount,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ShimmerCard(height: 180, borderRadius: const BorderRadius.vertical(top: Radius.circular(20))),
              const SizedBox(height: 12),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  ShimmerCard(height: 20, width: 150),
                  ShimmerCard(height: 20, width: 80),
                ],
              ),
              const SizedBox(height: 8),
              const ShimmerCard(height: 15, width: 220),
            ],
          ),
        );
      },
    );
  }
}
