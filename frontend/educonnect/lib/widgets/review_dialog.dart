import 'package:flutter/material.dart';

class ReviewDialog extends StatefulWidget {
  final String entityName;
  const ReviewDialog({super.key, required this.entityName});

  @override
  State<ReviewDialog> createState() => _ReviewDialogState();
}

class _ReviewDialogState extends State<ReviewDialog> {
  int _rating = 0;
  final TextEditingController _commentController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text("Write a Review", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text("How was your experience at ${widget.entityName}?", textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 20),
            
            /// Stars
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(5, (index) {
                return IconButton(
                  icon: Icon(
                    index < _rating ? Icons.star : Icons.star_border,
                    color: Colors.orange,
                    size: 32,
                  ),
                  onPressed: () => setState(() => _rating = index + 1),
                );
              }),
            ),
            
            const SizedBox(height: 15),
            
            TextField(
              controller: _commentController,
              maxLines: 3,
              onChanged: (v) => setState(() {}),
              decoration: InputDecoration(
                hintText: "Share your thoughts...",
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: isDark ? Colors.white10 : Colors.grey.shade50,
              ),
            ),
            
            const SizedBox(height: 25),
            
            Row(
              children: [
                Expanded(
                  child: TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text("Cancel"),
                  ),
                ),
                Expanded(
                  child: ElevatedButton(
                    onPressed: (_rating == 0 || _commentController.text.trim().isEmpty) ? null : () {
                      Navigator.pop(context, {
                        'rating': _rating, 
                        'comment': _commentController.text.trim()
                      });
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      disabledBackgroundColor: Colors.deepPurple.withOpacity(0.3),
                    ),
                    child: const Text("Post Review"),
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
