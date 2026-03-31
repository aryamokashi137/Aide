import 'package:flutter/material.dart';

class EducationDetailsPage extends StatelessWidget {
  final String name;
  final String category;
  final String image;
  final String location;
  final String fees;
  final String rating;

  const EducationDetailsPage({
    super.key,
    required this.name,
    required this.category,
    required this.image,
    required this.location,
    required this.fees,
    required this.rating,
  });

  Widget sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    );
  }

  Widget infoCard({required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300), // 🔥 border style
        borderRadius: BorderRadius.circular(12),
      ),
      child: child,
    );
  }

  Widget contactSection() {
    return infoCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text("Contact Information",
              style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Row(children: [Icon(Icons.phone_outlined), SizedBox(width: 8), Text("+91 9876543210")]),
          Row(children: [Icon(Icons.email_outlined), SizedBox(width: 8), Text("admissions@edu.com")]),
          Row(children: [Icon(Icons.language_outlined), SizedBox(width: 8), Text("www.edu.com")]),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: Colors.white,

        /// APPLY BUTTON
        bottomNavigationBar: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: const Text("Apply Now"),
          ),
        ),

        body: Column(
          children: [
            /// HEADER IMAGE
            Stack(
              children: [
                Image.network(
                  image,
                  height: 220,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
                Positioned(
                  top: 40,
                  left: 12,
                  child: CircleAvatar(
                    backgroundColor: Colors.white,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                ),
              ],
            ),

            /// CONTENT
            Expanded(
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(name,
                            style: const TextStyle(
                                fontSize: 20, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        Text("⭐ $rating"),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            const Icon(Icons.location_on_outlined, size: 16),
                            const SizedBox(width: 6),
                            Expanded(child: Text(location)),
                          ],
                        ),
                      ],
                    ),
                  ),

                  /// TABS
                  const TabBar(
                    labelColor: Colors.black,
                    indicatorColor: Colors.deepPurple,
                    tabs: [
                      Tab(text: "Overview"),
                      Tab(text: "Admission"),
                      Tab(text: "Reviews"),
                    ],
                  ),

                  /// TAB CONTENT (SCROLLABLE)
                  Expanded(
                    child: TabBarView(
                      children: [
                        /// OVERVIEW
                        SingleChildScrollView(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              sectionTitle("About"),
                              infoCard(
                                child: const Text(
                                  "Modern institution with strong academics and facilities.",
                                ),
                              ),

                              sectionTitle("Courses"),
                              infoCard(
                                child: Column(
                                  children: const [
                                    ListTile(
                                        leading: Icon(Icons.science_outlined),
                                        title: Text("Science")),
                                    ListTile(
                                        leading: Icon(Icons.business_outlined),
                                        title: Text("Commerce")),
                                    ListTile(
                                        leading: Icon(Icons.palette_outlined),
                                        title: Text("Arts")),
                                  ],
                                ),
                              ),

                              sectionTitle("Facilities"),
                              infoCard(
                                child: Column(
                                  children: const [
                                    ListTile(
                                        leading: Icon(Icons.menu_book_outlined),
                                        title: Text("Library")),
                                    ListTile(
                                        leading: Icon(Icons.computer_outlined),
                                        title: Text("Computer Lab")),
                                    ListTile(
                                        leading: Icon(Icons.sports_soccer),
                                        title: Text("Sports Ground")),
                                  ],
                                ),
                              ),

                              contactSection(),
                            ],
                          ),
                        ),

                        /// ADMISSION
                        SingleChildScrollView(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              sectionTitle("Fees"),
                              infoCard(child: Text(fees)),

                              sectionTitle("Process"),
                              infoCard(
                                child: const Text(
                                  "1. Apply\n2. Documents\n3. Test\n4. Admission",
                                ),
                              ),

                              contactSection(),
                            ],
                          ),
                        ),

                        /// REVIEWS
                        SingleChildScrollView(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              infoCard(
                                child: Column(
                                  children: const [
                                    ListTile(
                                      leading:
                                          CircleAvatar(child: Text("A")),
                                      title: Text("Amit"),
                                      subtitle:
                                          Text("Good college environment"),
                                    ),
                                    ListTile(
                                      leading:
                                          CircleAvatar(child: Text("P")),
                                      title: Text("Priya"),
                                      subtitle:
                                          Text("Nice infrastructure"),
                                    ),
                                  ],
                                ),
                              ),

                              contactSection(),
                            ],
                          ),
                        ),
                      ],
                    ),
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