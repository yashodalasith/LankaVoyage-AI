PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    district TEXT NOT NULL,
    category TEXT NOT NULL,
    estimated_cost_lkr INTEGER NOT NULL,
    avg_duration_hours REAL NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_city TEXT NOT NULL,
    to_city TEXT NOT NULL,
    mode TEXT NOT NULL,
    avg_fare_lkr INTEGER NOT NULL,
    avg_duration_hours REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,
    location TEXT NOT NULL,
    min_cost_lkr INTEGER NOT NULL,
    max_cost_lkr INTEGER NOT NULL,
    notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS distances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_city TEXT NOT NULL,
    to_city TEXT NOT NULL,
    distance_km INTEGER NOT NULL,
    travel_time_hours REAL NOT NULL
);

DELETE FROM attractions;
DELETE FROM transport;
DELETE FROM costs;
DELETE FROM distances;

INSERT INTO attractions (name, location, district, category, estimated_cost_lkr, avg_duration_hours, description) VALUES
('Sigiriya Rock Fortress', 'Sigiriya', 'Matale', 'heritage', 5000, 3.0, 'Ancient rock fortress with frescoes and summit ruins.'),
('Pidurangala Rock', 'Sigiriya', 'Matale', 'hiking', 1500, 2.5, 'Popular sunrise and sunset hike with Sigiriya views.'),
('Temple of the Tooth', 'Kandy', 'Kandy', 'heritage', 2500, 2.0, 'Sacred Buddhist temple housing a tooth relic.'),
('Royal Botanical Gardens', 'Peradeniya', 'Kandy', 'nature', 3000, 3.0, 'Large botanical collection near Kandy.'),
('Ambuluwawa Tower', 'Gampola', 'Kandy', 'viewpoint', 2000, 2.0, 'Narrow spiral tower with panoramic mountain views.'),
('Nine Arches Bridge', 'Ella', 'Badulla', 'scenic', 500, 1.5, 'Iconic colonial railway bridge in lush hills.'),
('Little Adams Peak', 'Ella', 'Badulla', 'hiking', 0, 2.0, 'Beginner-friendly hike with scenic ridge views.'),
('Ella Rock', 'Ella', 'Badulla', 'hiking', 0, 5.0, 'Longer hike offering expansive hill country vistas.'),
('Ravana Falls', 'Ella', 'Badulla', 'nature', 0, 1.0, 'Roadside waterfall near Ella town.'),
('Yala National Park Safari', 'Yala', 'Hambantota', 'wildlife', 14000, 5.0, 'Jeep safari known for leopard sightings.'),
('Udawalawe National Park', 'Udawalawe', 'Ratnapura', 'wildlife', 12000, 4.5, 'Safari park famous for elephants.'),
('Minneriya National Park', 'Habarana', 'Polonnaruwa', 'wildlife', 11000, 4.0, 'Seasonal elephant gathering near Minneriya tank.'),
('Galle Fort', 'Galle', 'Galle', 'heritage', 0, 3.0, 'UNESCO listed colonial fort with ramparts.'),
('Jungle Beach', 'Unawatuna', 'Galle', 'beach', 0, 3.0, 'Small beach with calm waters and jungle edge.'),
('Mirissa Whale Watching', 'Mirissa', 'Matara', 'marine', 18000, 5.0, 'Boat trips to see blue whales and dolphins.'),
('Weligama Surf Spot', 'Weligama', 'Matara', 'adventure', 7000, 3.0, 'Beginner surf breaks and board rentals.'),
('Horton Plains and Worlds End', 'Nuwara Eliya', 'Nuwara Eliya', 'hiking', 9000, 4.5, 'Highland plateau trail ending at dramatic cliff.'),
('Gregory Lake', 'Nuwara Eliya', 'Nuwara Eliya', 'leisure', 2000, 2.0, 'Lake activities and city-side relaxation.'),
('Pedro Tea Estate', 'Nuwara Eliya', 'Nuwara Eliya', 'tea', 1500, 1.5, 'Tea factory tour and tasting experience.'),
('Pinnawala Elephant Orphanage', 'Pinnawala', 'Kegalle', 'wildlife', 3500, 2.5, 'Elephant care center with river bathing sessions.'),
('Anuradhapura Ancient City', 'Anuradhapura', 'Anuradhapura', 'heritage', 4500, 4.5, 'Sacred city with stupas and monastic ruins.'),
('Polonnaruwa Ruins', 'Polonnaruwa', 'Polonnaruwa', 'heritage', 4200, 4.0, 'Medieval capital with preserved stone carvings.'),
('Dambulla Cave Temple', 'Dambulla', 'Matale', 'heritage', 2000, 2.0, 'Cave shrine complex with Buddhist murals.'),
('Arugam Bay Beach', 'Arugam Bay', 'Ampara', 'beach', 0, 4.0, 'Eastern surf town with laid-back atmosphere.'),
('Nilaveli Beach', 'Nilaveli', 'Trincomalee', 'beach', 0, 4.0, 'Clear water beach near Trincomalee.'),
('Pigeon Island Snorkeling', 'Nilaveli', 'Trincomalee', 'marine', 8000, 3.5, 'Marine park known for coral and reef sharks.'),
('Jaffna Fort', 'Jaffna', 'Jaffna', 'heritage', 500, 2.0, 'Portuguese and Dutch era fort in Jaffna city.'),
('Nallur Kandaswamy Kovil', 'Jaffna', 'Jaffna', 'heritage', 0, 1.5, 'Major Hindu temple with ornate architecture.'),
('Kalpitiya Dolphin Watching', 'Kalpitiya', 'Puttalam', 'marine', 12000, 4.0, 'Boat tours for spinner dolphin sightings.'),
('Kitulgala White Water Rafting', 'Kitulgala', 'Kegalle', 'adventure', 9000, 3.0, 'River rafting and adventure activities.'),
('Sinharaja Rainforest Trek', 'Sinharaja', 'Ratnapura', 'nature', 6500, 5.0, 'Biodiversity hotspot and UNESCO rainforest reserve.');

INSERT INTO transport (from_city, to_city, mode, avg_fare_lkr, avg_duration_hours) VALUES
('Colombo', 'Kandy', 'train', 1200, 3.0),
('Colombo', 'Kandy', 'bus', 500, 3.5),
('Colombo', 'Ella', 'train', 1600, 7.0),
('Colombo', 'Ella', 'bus', 1100, 6.5),
('Colombo', 'Galle', 'train', 800, 2.5),
('Colombo', 'Galle', 'bus', 600, 2.5),
('Kandy', 'Ella', 'train', 1000, 6.0),
('Ella', 'Yala', 'car', 12000, 2.5),
('Kandy', 'Sigiriya', 'car', 9000, 2.0),
('Colombo', 'Nuwara Eliya', 'bus', 1500, 5.5),
('Nuwara Eliya', 'Ella', 'train', 700, 3.0),
('Colombo', 'Anuradhapura', 'train', 1000, 4.5),
('Colombo', 'Jaffna', 'train', 1800, 7.5),
('Colombo', 'Trincomalee', 'bus', 1700, 6.5);

INSERT INTO costs (item_type, location, min_cost_lkr, max_cost_lkr, notes) VALUES
('accommodation_budget', 'Ella', 6000, 12000, 'Per night for two in budget guesthouses.'),
('accommodation_midrange', 'Ella', 13000, 25000, 'Per night for two in boutique hotels.'),
('accommodation_budget', 'Kandy', 7000, 13000, 'Per night for two in city hotels.'),
('accommodation_budget', 'Galle', 9000, 18000, 'Per night for two near fort or beachside.'),
('meal_per_person', 'Sri Lanka', 1200, 3500, 'Average meal cost depending on venue.'),
('private_taxi_day_hire', 'Sri Lanka', 18000, 28000, 'Includes fuel and driver in most regions.'),
('safari_jeep_shared', 'Yala', 9000, 15000, 'Shared jeep rates vary by season.');

INSERT INTO distances (from_city, to_city, distance_km, travel_time_hours) VALUES
('Colombo', 'Kandy', 115, 3.0),
('Colombo', 'Ella', 210, 6.5),
('Colombo', 'Sigiriya', 170, 4.5),
('Kandy', 'Ella', 135, 5.5),
('Ella', 'Yala', 95, 2.5),
('Colombo', 'Galle', 130, 2.5),
('Colombo', 'Nuwara Eliya', 170, 5.0),
('Colombo', 'Anuradhapura', 205, 4.5),
('Colombo', 'Trincomalee', 265, 6.0),
('Colombo', 'Jaffna', 395, 8.0);
