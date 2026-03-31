import 'package:flutter/material.dart';

class PGDetailsPage extends StatelessWidget {
  const PGDetailsPage({super.key});

  Widget sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 12),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 17,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget infoCard({required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: child,
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: Colors.white,

        /// Schedule Visit Button
        bottomNavigationBar: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton.icon(
            icon: const Icon(Icons.calendar_month),
            label: const Text("Schedule Visit"),
            style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 14),
            backgroundColor: Colors.purple,
            foregroundColor: Colors.white, // icon + text color
            textStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
            onPressed: () async {

              /// Select Date
              DateTime? selectedDate = await showDatePicker(
                context: context,
                initialDate: DateTime.now(),
                firstDate: DateTime.now(),
                lastDate: DateTime(2030),
              );

              if (selectedDate == null) return;

              /// Select Time
              TimeOfDay? selectedTime = await showTimePicker(
                context: context,
                initialTime: TimeOfDay.now(),
              );

              if (selectedTime == null) return;

              /// Confirmation Popup
              showDialog(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                    title: const Text("Visit Scheduled"),
                    content: Text(
                      "Your visit is scheduled on\n"
                      "${selectedDate.day}/${selectedDate.month}/${selectedDate.year}"
                      " at ${selectedTime.format(context)}",
                    ),
                    actions: [
                      TextButton(
                        onPressed: () {
                          Navigator.pop(context);
                        },
                        child: const Text("OK"),
                      )
                    ],
                  );
                },
              );
            },
          ),
        ),

        appBar: AppBar(
          elevation: 0,
          backgroundColor: Colors.white,
          iconTheme: const IconThemeData(color: Colors.black),
          title: const Text(
            "PG Details",
            style: TextStyle(color: Colors.black),
          ),
        ),

        body: Column(
          children: [

            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [

                    /// Image
                    Image.network(
                      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                      height: 250,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),

                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [

                          const Text(
                            "Comfort Living PG",
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          const SizedBox(height: 8),

                          Row(
                            children: const [
                              Icon(Icons.star,
                                  color: Colors.orange, size: 18),
                              SizedBox(width: 4),
                              Text("4.5"),
                              SizedBox(width: 6),
                              Text("(78 reviews)",
                                  style: TextStyle(color: Colors.grey)),
                            ],
                          ),

                          const SizedBox(height: 10),

                          Row(
                            children: const [
                              Icon(Icons.location_on_outlined,
                                  size: 16, color: Colors.grey),
                              SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  "45 HSR Layout, Sector 2, Bangalore",
                                  style: TextStyle(color: Colors.grey),
                                ),
                              ),
                            ],
                          ),

                          const SizedBox(height: 20),

                          /// Pricing
                          const Text(
                            "Pricing",
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          const SizedBox(height: 10),

                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.spaceBetween,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: Colors.purple.shade50,
                                  borderRadius:
                                      BorderRadius.circular(12),
                                ),
                                child: const Column(
                                  children: [
                                    Icon(Icons.currency_rupee),
                                    SizedBox(height: 6),
                                    Text("₹8,500 / Month"),
                                  ],
                                ),
                              ),

                              Container(
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade50,
                                  borderRadius:
                                      BorderRadius.circular(12),
                                ),
                                child: const Column(
                                  children: [
                                    Icon(Icons.home),
                                    SizedBox(height: 6),
                                    Text("Deposit ₹10,000"),
                                  ],
                                ),
                              ),
                            ],
                          ),

                          const SizedBox(height: 25),

                          /// Tabs
                          const TabBar(
                            labelColor: Colors.black,
                            indicatorColor: Colors.purple,
                            tabs: [
                              Tab(text: "Overview"),
                              Tab(text: "Amenities"),
                              Tab(text: "Reviews"),
                            ],
                          ),

                          const SizedBox(height: 15),

                          SizedBox(
                            height: 420,
                            child: TabBarView(
                              children: [

                                /// OVERVIEW TAB
                                SingleChildScrollView(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [

                                      sectionTitle("Description"),
                                      infoCard(
                                        child: const Text(
                                          "Comfort Living PG offers clean rooms, healthy food, high-speed WiFi and a peaceful environment. Perfect for students and working professionals.",
                                        ),
                                      ),

                                      sectionTitle("House Rules"),
                                      infoCard(
                                        child: Column(
                                          children: const [
                                            ListTile(
                                              leading: Icon(Icons.access_time),
                                              title: Text(
                                                  "Gate closes at 11 PM"),
                                            ),
                                            ListTile(
                                              leading:
                                                  Icon(Icons.smoke_free),
                                              title: Text(
                                                  "No smoking inside rooms"),
                                            ),
                                            ListTile(
                                              leading: Icon(Icons.people),
                                              title: Text(
                                                  "No outside guests allowed"),
                                            ),
                                          ],
                                        ),
                                      ),

                                      sectionTitle("Nearby Places"),
                                      infoCard(
                                        child: Column(
                                          children: const [
                                            ListTile(
                                              leading:
                                                  Icon(Icons.business),
                                              title: Text(
                                                  "Tech Park - 1 km"),
                                            ),
                                            ListTile(
                                              leading: Icon(
                                                  Icons.restaurant),
                                              title: Text(
                                                  "Food Street - 500 m"),
                                            ),
                                            ListTile(
                                              leading: Icon(Icons
                                                  .local_hospital),
                                              title: Text(
                                                  "Hospital - 800 m"),
                                            ),
                                          ],
                                        ),
                                      ),

                                      sectionTitle("Owner Contact"),
                                      infoCard(
                                        child: Column(
                                          children: const [
                                            ListTile(
                                              leading:
                                                  Icon(Icons.person),
                                              title:
                                                  Text("Mr. Ramesh"),
                                            ),
                                            ListTile(
                                              leading:
                                                  Icon(Icons.phone),
                                              title: Text(
                                                  "+91 9876543210"),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),

                                /// AMENITIES TAB
                                SingleChildScrollView(
                                  child: Column(
                                    children: const [

                                      ListTile(
                                        leading: Icon(Icons.wifi,
                                            color: Colors.blue),
                                        title: Text("High Speed WiFi"),
                                      ),
                                      Divider(),

                                      ListTile(
                                        leading: Icon(
                                            Icons.restaurant,
                                            color: Colors.orange),
                                        title:
                                            Text("Daily Meals Included"),
                                      ),
                                      Divider(),

                                      ListTile(
                                        leading: Icon(
                                            Icons
                                                .local_laundry_service,
                                            color: Colors.purple),
                                        title:
                                            Text("Laundry Service"),
                                      ),
                                      Divider(),

                                      ListTile(
                                        leading: Icon(
                                            Icons.local_parking,
                                            color: Colors.green),
                                        title:
                                            Text("Parking Facility"),
                                      ),
                                      Divider(),

                                      ListTile(
                                        leading: Icon(Icons.security,
                                            color: Colors.red),
                                        title: Text("24x7 Security"),
                                      ),
                                      Divider(),

                                      ListTile(
                                        leading: Icon(
                                            Icons.cleaning_services,
                                            color: Colors.teal),
                                        title:
                                            Text("Housekeeping"),
                                      ),
                                    ],
                                  ),
                                ),

                                /// REVIEWS TAB
                                Column(
                                  children: const [

                                    ListTile(
                                      leading: CircleAvatar(
                                        child: Text("A"),
                                      ),
                                      title: Text("Akash"),
                                      subtitle: Text(
                                          "Very clean rooms and good food."),
                                    ),

                                    ListTile(
                                      leading: CircleAvatar(
                                        child: Text("R"),
                                      ),
                                      title: Text("Rohit"),
                                      subtitle: Text(
                                          "Affordable PG near office."),
                                    ),
                                  ],
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
            ),
          ],
        ),
      ),
    );
  }
}

