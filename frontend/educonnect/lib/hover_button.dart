import 'package:flutter/material.dart';

class HoverButton extends StatefulWidget {
  final String text;
  final VoidCallback onPressed;
  final double height;

  const HoverButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.height = 50,
  });

  @override
  State<HoverButton> createState() => _HoverButtonState();
}

class _HoverButtonState extends State<HoverButton> {
  bool isHover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHover = true),
      onExit: (_) => setState(() => isHover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        height: widget.height,
        width: double.infinity,
        decoration: BoxDecoration(
          color: isHover ? Colors.blue.shade700 : Colors.blue,
          borderRadius: BorderRadius.circular(30),
          boxShadow: isHover
              ? [
                  BoxShadow(
                    color: Colors.blue.withOpacity(0.4),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  )
                ]
              : [],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(30),
            onTap: widget.onPressed,
            child: Center(
              child: Text(
                widget.text,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}