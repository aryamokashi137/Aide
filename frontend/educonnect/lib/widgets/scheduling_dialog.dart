import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class SchedulingDialog extends StatefulWidget {
  final String entityName;
  const SchedulingDialog({super.key, required this.entityName});

  @override
  State<SchedulingDialog> createState() => _SchedulingDialogState();
}

class _SchedulingDialogState extends State<SchedulingDialog> {
  DateTime selectedDate = DateTime.now().add(const Duration(days: 1));
  String preferredTime = "Morning";
  final TextEditingController _msgController = TextEditingController();

  final List<String> times = ["Morning", "Afternoon", "Evening"];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AlertDialog(
      title: Text("Schedule Visit: ${widget.entityName}"),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Select Date", style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            InkWell(
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: selectedDate,
                  firstDate: DateTime.now(),
                  lastDate: DateTime.now().add(const Duration(days: 90)),
                );
                if (date != null) setState(() => selectedDate = date);
              },
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade400),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today, size: 20),
                    const SizedBox(width: 10),
                    Text(DateFormat('EEE, MMM d, yyyy').format(selectedDate)),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),
            const Text("Preferred Time", style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: times.map((t) => Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(t),
                  selected: preferredTime == t,
                  onSelected: (val) { if (val) setState(() => preferredTime = t); },
                ),
              )).toList(),
            ),

            const SizedBox(height: 16),
            const Text("Optional Message", style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _msgController,
              decoration: InputDecoration(
                hintText: "How many rooms?",
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
              maxLines: 2,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text("CANCEL")),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context, {
              'date': selectedDate,
              'time': preferredTime,
              'message': _msgController.text,
            });
          },
          child: const Text("CONFIRM"),
        ),
      ],
    );
  }
}
