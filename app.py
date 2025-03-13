import os
import csv
import re
from math import ceil
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random

app = Flask(__name__)

# State abbreviation to full name mapping
STATE_NAMES = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'DC': 'District of Columbia'
}

# Create a reverse mapping from full name to abbreviation
STATE_ABBRS = {name: abbr for abbr, name in STATE_NAMES.items()}

# Create a lowercase mapping for state names
STATE_NAMES_LOWER = {name.lower(): name for name in STATE_NAMES.values()}

# Function to create a URL-friendly slug from a tour title
def create_tour_slug(title):
    # Use the full title instead of just the part before the colon
    slug = title.lower()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Trim to a reasonable length
    slug = slug[:100].strip('-')
    
    return slug

# Process tour data to format values
def process_tour_data(tour):
    processed_tour = dict(tour)
    
    # Format review count to remove decimal
    if processed_tour.get('Reviews Count'):
        try:
            review_count = float(processed_tour['Reviews Count'])
            processed_tour['Reviews Count'] = int(review_count)
        except (ValueError, TypeError):
            pass
    
    # Fix dollar sign in price
    if processed_tour.get('Price'):
        try:
            # Remove any existing dollar signs
            price_str = str(processed_tour['Price'])
            price_str = price_str.replace('$', '')
            # Store as a numeric value without dollar sign
            processed_tour['Price'] = float(price_str)
        except (ValueError, TypeError):
            pass
    
    # Ensure Image URL is None if empty
    if processed_tour.get('Image URL') and (processed_tour['Image URL'] == '' or processed_tour['Image URL'].isspace()):
        processed_tour['Image URL'] = None
    
    # Generate a slug for the tour
    if processed_tour.get('Title'):
        processed_tour['Slug'] = create_tour_slug(processed_tour['Title'])
    
    # Replace description with a template
    if processed_tour.get('Title'):
        processed_tour['Description'] = generate_tour_description(processed_tour['Title'])
    
    return processed_tour

# Tour description templates
TOUR_DESCRIPTION_TEMPLATES = [
    """Discover {location} with guides who truly know the place. They're locals who don't just show you around—they share the stories that bring every stop in {location} to life. You'll hear interesting facts, get insider tips, and learn about the culture in a way you wouldn't if you explored alone. Have questions? Ask away. Our guides love a good conversation, and no question is too small. We believe that a great tour starts with a great experience from the moment you book. That's why our customer service team is always on hand to help with any questions or special requests. Need to change your booking? Want advice about {location}? No problem. Our guests often tell us how simple and smooth the booking process was, and how supported they felt throughout their entire trip. We care about making sure your tour is relaxed, fun, and easy—just show up and let us handle the details. Most people leave our tours feeling like they learned something new, saw more than they expected, and had a few good laughs along the way. That's what makes a great day out in {location}.""",
    
    """If you're looking to explore {location} without any hassle, this is the tour for you. Our guides are locals who know the best spots and love sharing stories that make each place in {location} more than just a photo opportunity. You'll learn about the culture, the history, and the little things that make {location} unique. Don't be shy—if you've got questions, ask! Our guides are passionate about what they do, and they love sharing local insights. We also know that a great tour starts long before you arrive, so our customer service team is here to make booking simple and stress-free. Need to change a detail or add something last-minute? We've got it covered. Many of our past guests say how easy it was to book and how helpful the team was from start to finish. We're about keeping it simple, fun, and personal. No confusing processes, no waiting around, just a smooth experience. All you need to do is show up ready to enjoy {location}. We'll handle the rest, so you can focus on the fun.""",
    
    """Booking a tour in {location} with us means you're signing up for a stress-free, fun day with guides who really know their stuff. They'll take you beyond the usual tourist stops and share the stories and history that make each location in {location} memorable. It's not about rushing from one place to the next—it's about really getting to know the area and hearing the little details that make it special. Have questions? Our guides love a good chat, and they're happy to answer anything, whether it's about the landmarks, the local culture, or just where to find the best coffee in {location}. We also take customer service seriously. From the moment you book, our team is ready to help with any questions or special requests. Need to adjust something? We make it easy. Most people tell us the booking process was smooth, and they appreciated how well they were looked after. You'll leave knowing more, seeing more, and with stories worth sharing. That's the kind of day we aim to give you in {location}.""",
    
    """Exploring {location} with us is all about making your day fun, simple, and packed with good stories. Our guides know the area well, and they're not just there to show you the spots—they're there to give you real insight into {location}. They'll share stories that bring each place to life and will happily answer any questions you have. We believe every tour should feel personal and relaxed, with plenty of time to enjoy each stop. On top of that, we take pride in our customer service. From the moment you book, our team is here to make the process smooth and stress-free. Got last-minute changes? No problem. Need advice about the best spots in {location}? Just ask. Many of our guests say that the booking process was one of the easiest they've experienced, and they felt well cared for the whole way. We've designed everything to be straightforward and hassle-free, so all you need to do is show up and enjoy the day. You'll walk away with great memories, fun stories, and maybe even a few new friends. That's what makes a tour in {location} worth it.""",
    
    """Our {location} tours are designed for people who want a relaxed, easygoing experience without missing out on the details that make a place special. Our guides know the local history, the hidden spots, and the stories that add something extra to each stop in {location}. They love answering questions, sharing personal insights, and making sure you feel like more than just a face in the crowd. You'll leave knowing more about {location} than you expected and with plenty of good stories to tell. Plus, our customer service team is always ready to help, from booking to the end of your tour. We know plans can change, so we're flexible and quick to assist. Most guests tell us they were surprised at how simple and smooth the booking process was. That's the goal—to keep things easy so you can focus on enjoying yourself. No hassle, no stress, just a day that's fun, informative, and memorable.""",
    
    """When you book a tour in {location} with us, you're not just getting a guide—you're getting someone who knows the stories, the local history, and the best spots to visit in {location}. Our guides are passionate about what they do and love answering any questions you have along the way. Want to know the best place for lunch? Or the history behind a landmark? Just ask. Our tours are designed to be relaxed, fun, and full of great moments. Plus, our customer service team is always here to help. From booking to your final stop, we make it simple. If plans change or you have special requests, we're just a message away. Most of our guests tell us how easy the process was and how much they appreciated the support. We're about keeping it smooth and hassle-free, so all you have to do is show up and enjoy the best of {location}.""",
    
    """If you're looking for an easy, fun, and informative way to explore {location}, you're in the right place. Our guides are locals who know {location} inside out. They'll show you the best spots, share cool facts, and give you a real sense of what makes the area unique. Got questions? Just ask. We love sharing little-known details that make the experience even better. And if you need help with anything, our customer service team is always ready. Booking is simple, and most guests tell us it was one of the easiest experiences they've had. From start to finish, we focus on keeping things smooth, easy, and fun. No complicated steps, no long waits—just a relaxed tour where you can enjoy the day and take in the best of {location}.""",
    
    """Exploring {location} should feel fun, simple, and memorable—and that's exactly what we're here to offer. Our tours are designed to give you more than just the standard stops. We believe the best way to experience {location} is by getting to know the stories and the local culture that make it special. Our guides aren't just knowledgeable—they're passionate about sharing what makes {location} unique. They'll point out the details most people miss and share the kind of fun facts and personal stories that bring each location to life.

Have a question about the area? Curious about local traditions or the best food spots? Just ask. Our guides love answering questions and sharing tips to help you make the most of your day. And if you need anything else, our customer service team is always ready to help. From the moment you book, we're here to make the process smooth and easy. Need to adjust a booking or add a last-minute change? No problem. We know things come up, and we're quick to respond and assist.

Many of our past guests have told us how simple and stress-free the entire experience was—from the first click to the final stop. That's what we aim for: an easy, laid-back experience that lets you focus on the fun parts. All you have to do is show up, relax, and enjoy discovering {location}. We'll take care of the details, so your day is packed with great stories and good memories.""",
    
    """A tour of {location} should feel like an easy, fun day spent with friends—and that's exactly what we aim to give you. Our guides are locals who know {location} inside and out. They don't just show you the main attractions; they'll tell you about the hidden corners, local legends, and stories that bring the place to life. They love what they do and are always happy to answer questions or share fun facts you won't find in a guidebook.

We know that planning a trip can feel overwhelming, but booking with us is designed to be simple and stress-free. Our customer service team is here to make the process as smooth as possible. Have a question before booking? Need to adjust your plans? We're quick to respond and always ready to help. Most of our guests tell us they were surprised at how easy it was to book and how supported they felt throughout the experience.

We've designed every part of our tour to make sure you feel relaxed and well taken care of. From the moment you join us, our guides focus on creating a fun, personal experience that goes beyond just seeing the sights. It's about connecting with {location}, learning its stories, and walking away with memories that stick. So show up ready for a great day, and we'll handle the rest.""",
    
    """Booking a tour with us in {location} means you're choosing a stress-free, fun, and personal way to explore. Our guides know {location} better than anyone. They're not just pointing out landmarks—they're sharing stories, answering questions, and helping you see the place in a whole new way. They love talking about local traditions, hidden spots, and the kind of fun details that make the day memorable.

Got questions? Ask away. Our guides love a good chat, and they're always happy to share local tips or fun facts. And when it comes to booking, we make it simple. Our customer service team is ready to help with any questions, special requests, or last-minute changes. We know travel plans can change, and we're here to keep things flexible and easy. Many of our guests have told us they were surprised at how smooth the entire process was. From the first booking step to the final stop of the tour, we're focused on making your experience feel simple and enjoyable.

We believe that the best kind of tour is one where you feel like you're hanging out with friends—where the pace is relaxed, the conversations are good, and the memories last long after the tour is over. That's what we aim for every day in {location}. All you need to do is show up and enjoy yourself. We'll handle the details.""",
    
    """When you're exploring a new place like {location}, you want the experience to feel authentic, relaxed, and easy to enjoy. That's why our tours are designed to be more than just ticking off landmarks. Our guides are locals who know the stories, the traditions, and the little details that make {location} unique. They love sharing those stories and answering any questions along the way—whether it's about history, culture, or the best place to grab lunch after the tour.

We know that booking should be just as easy as the tour itself, which is why our customer service team is always ready to help. Need to change your booking? Have a last-minute question? No problem. We're quick to respond and happy to assist. Guests often tell us how smooth and simple the booking process was, and how supported they felt from start to finish.

Our goal is to make sure you have the kind of day where you're not just seeing {location}, but actually connecting with it. Whether it's learning about its past, hearing local legends, or getting personal recommendations from your guide, it's all about making sure you leave with great memories. So relax, enjoy the day, and let us handle the rest.""",
    
    """In {location}, every corner has a story, and our guides are here to share those stories with you. They don't just take you to the big landmarks—they'll show you the side streets, the hidden gems, and the places that locals love. They know the history, the traditions, and all the fun little facts that make {location} unique. And they're always happy to answer questions or share a personal story that adds to the experience.

Booking with us is designed to be as easy and stress-free as the tour itself. Our customer service team is ready to help with any questions, changes, or special requests. We know travel plans can change, and we keep things flexible to make sure you get the best experience. Most of our guests tell us how smooth the process was and how supported they felt along the way.

We want you to feel like you're spending the day with a friend who knows the area well. Someone who can show you the best spots, share great stories, and make sure you leave with memories worth sharing. That's how we approach every tour in {location}—personal, relaxed, and full of fun moments you'll remember long after the day is done.""",
    
    """Discover the real {location} with guides who know the area like the back of their hand. Our tours aren't just about pointing at landmarks and moving on. We focus on sharing the stories, local history, and hidden gems that make {location} unique. Our guides are friendly, approachable, and always ready to answer your questions—whether it's about the culture, the local food scene, or the best place to hang out after the tour. We believe that the little details matter, and we're here to make your day feel personal and meaningful.

Booking is designed to be quick and easy, with our customer service team always ready to assist. Whether you need to change something last-minute or have questions before your tour, we're just a message away. Guests often tell us how smooth the entire booking process was, and how supported they felt from start to finish. That's the kind of service we aim to provide—stress-free and reliable.

We handle the details so you can focus on enjoying {location}. Our goal is to make sure you leave with more than just photos. You'll leave with stories, local insights, and memories that stick. All you have to do is show up, relax, and let us take care of the rest.""",
    
    """When you think of touring {location}, it shouldn't feel rushed or stressful—it should feel like a laid-back day spent with people who love the place and want you to love it too. That's why we focus on making every tour easy, fun, and personal. Our guides are locals who don't just show you around—they share the stories and little-known facts that make {location} special. They'll take you beyond the obvious stops, helping you connect with the place in a real, memorable way.

We also know that good service starts long before the tour, which is why our customer service team is always available to help with booking, special requests, or last-minute questions. Guests tell us they were surprised by how smooth the process was and how supported they felt from start to finish.

You won't have to worry about the small stuff—we've got it covered. All you need to do is show up and enjoy learning about {location} through the eyes of a local. By the end of the day, we hope you'll feel like you've experienced the best of what the area has to offer, in a way that feels genuine and relaxed.""",
    
    """A great tour is about more than just walking around—it's about connecting with the place, hearing the stories, and feeling like you've really learned something new. That's exactly what we offer in {location}. Our guides know the city inside and out, and they're passionate about sharing the little details that most people miss. They're always happy to answer questions, offer tips, and make the day feel personal and engaging.

We also believe that a great experience starts with great service. Our customer service team is always available to help, whether you're booking, changing details, or just asking about the best time to visit a certain spot. Guests often tell us how smooth the booking process was and how easy it was to make adjustments when needed.

We keep things simple and stress-free, so you can focus on enjoying {location} without worrying about the details. By the end of the day, we hope you'll feel like you've seen a side of {location} that most people miss. The kind of tour that feels like a good conversation with a local friend—full of stories, laughs, and memories that stick.""",
    
    """Exploring {location} should feel easy, enjoyable, and personal—and that's exactly what we focus on. Our guides know {location} well and love sharing the kinds of stories and insights that you won't find in a guidebook. They'll point out hidden details, share fun facts, and answer any questions along the way. It's all about making the experience feel relaxed and personal, like hanging out with a friend who knows the area well.

We also know that good service starts long before the tour. That's why our customer service team is ready to help from the moment you start booking. Need to change your plans? Have a last-minute question? No problem. We're quick to respond and happy to help. Guests often tell us they were surprised by how easy and stress-free the booking process was, and how supported they felt from start to finish.

Our goal is simple: to make sure you enjoy every minute in {location}, from the first step of booking to the final stop on your tour. We'll handle the details so you can focus on the fun parts—like learning local stories, hearing interesting facts, and walking away with great memories.""",
    
    """When you join our tour in {location}, it's more than just visiting the main spots—it's about hearing the stories, learning the history, and understanding the culture in a way that feels personal and relaxed. Our guides are locals who know {location} well and love sharing their knowledge. They're always happy to answer questions, give recommendations, and share personal stories that bring the place to life.

We believe that a great tour starts with great service, which is why our customer service team is available from the moment you start booking. Need to change plans? Have questions about the tour? We're quick to respond and happy to help. Many guests tell us how easy the process was, and how much they appreciated the support along the way.

We've designed every part of the experience to be simple, smooth, and stress-free. That way, you can focus on enjoying {location} and walking away with good memories and fun stories. Just show up, relax, and let us take care of the rest."""
]

# Function to extract location from tour title and generate a description
def generate_tour_description(title):
    # Extract location from title
    location = extract_location_from_title(title)
    
    # Select a random template
    template = random.choice(TOUR_DESCRIPTION_TEMPLATES)
    
    # Replace {location} with the extracted location
    description = template.replace('{location}', location)
    
    return description

# Function to extract location from tour title
def extract_location_from_title(title):
    # List of common US locations (cities, parks, landmarks)
    common_locations = [
        'Yellowstone', 'Grand Canyon', 'Yosemite', 'Zion', 'Bryce Canyon', 'Arches', 
        'Canyonlands', 'Dead Horse', 'Moab', 'Las Vegas', 'New York', 'Manhattan', 
        'Brooklyn', 'Miami', 'Orlando', 'Chicago', 'Los Angeles', 'San Francisco', 
        'Seattle', 'Portland', 'Boston', 'Philadelphia', 'Washington DC', 'New Orleans', 
        'Nashville', 'Memphis', 'Austin', 'Dallas', 'Houston', 'Denver', 'Salt Lake City', 
        'Phoenix', 'Tucson', 'San Diego', 'Honolulu', 'Maui', 'Kauai', 'Big Island', 
        'Hawaii', 'Alaska', 'Anchorage', 'Fairbanks', 'Juneau', 'Sedona', 'Antelope Canyon',
        'Monument Valley', 'Niagara Falls', 'Acadia', 'Olympic', 'Glacier', 'Rocky Mountain',
        'Everglades', 'Key West', 'Savannah', 'Charleston', 'Atlanta', 'Asheville',
        'Santa Fe', 'Taos', 'Lake Tahoe', 'Napa Valley', 'Sonoma', 'Monterey', 'Carmel',
        'Santa Barbara', 'Palm Springs', 'Joshua Tree', 'Death Valley', 'Sequoia',
        'Redwood', 'Mount Rushmore', 'Badlands', 'Crater Lake', 'Mount Rainier',
        'North Cascades', 'Olympic Peninsula', 'San Juan Islands', 'Cape Cod',
        'Martha\'s Vineyard', 'Nantucket', 'Bar Harbor', 'White Mountains',
        'Green Mountains', 'Adirondacks', 'Catskills', 'Poconos', 'Outer Banks',
        'Hilton Head', 'Myrtle Beach', 'Gulf Shores', 'Destin', 'Clearwater',
        'St. Petersburg', 'St. Augustine', 'Sanibel Island', 'Captiva Island',
        'Smoky Mountains', 'Blue Ridge Mountains', 'Shenandoah', 'Mammoth Cave',
        'Hot Springs', 'Branson', 'Ozarks', 'Mackinac Island', 'Door County',
        'Wisconsin Dells', 'Mall of America', 'Mount Desert Island', 'Kennebunkport',
        'Newport', 'Providence', 'Mystic', 'New Haven', 'Annapolis', 'Baltimore',
        'Richmond', 'Williamsburg', 'Virginia Beach', 'Myrtle Beach', 'Hilton Head',
        'Savannah', 'Jekyll Island', 'St. Simons Island', 'Amelia Island',
        'St. Augustine', 'Daytona Beach', 'Cocoa Beach', 'Melbourne', 'Vero Beach',
        'West Palm Beach', 'Fort Lauderdale', 'Hollywood', 'Miami Beach', 'Key Largo',
        'Islamorada', 'Marathon', 'Big Pine Key', 'Key West', 'Dry Tortugas',
        'Sanibel Island', 'Captiva Island', 'Fort Myers', 'Naples', 'Marco Island',
        'Everglades City', 'Sarasota', 'St. Petersburg', 'Clearwater', 'Tampa',
        'Crystal River', 'Cedar Key', 'Apalachicola', 'Panama City Beach', 'Pensacola',
        'Gulf Shores', 'Mobile', 'Biloxi', 'Gulfport', 'New Orleans', 'Baton Rouge',
        'Lafayette', 'Natchez', 'Vicksburg', 'Memphis', 'Nashville', 'Chattanooga',
        'Knoxville', 'Gatlinburg', 'Pigeon Forge', 'Asheville', 'Charlotte',
        'Raleigh', 'Durham', 'Chapel Hill', 'Wilmington', 'Charleston', 'Myrtle Beach',
        'Hilton Head', 'Savannah', 'Atlanta', 'Athens', 'Augusta', 'Columbus',
        'Macon', 'Albany', 'Valdosta', 'Jacksonville', 'Tallahassee', 'Pensacola',
        'Destin', 'Panama City Beach', 'Apalachicola', 'Cedar Key', 'Crystal River',
        'Tampa', 'Clearwater', 'St. Petersburg', 'Sarasota', 'Fort Myers', 'Naples',
        'Marco Island', 'Everglades City', 'Miami', 'Fort Lauderdale', 'West Palm Beach',
        'Vero Beach', 'Melbourne', 'Cocoa Beach', 'Daytona Beach', 'St. Augustine',
        'Amelia Island', 'Jekyll Island', 'St. Simons Island', 'Brunswick', 'Savannah',
        'Tybee Island', 'Hilton Head', 'Beaufort', 'Charleston', 'Myrtle Beach',
        'Wilmington', 'Outer Banks', 'Virginia Beach', 'Norfolk', 'Williamsburg',
        'Richmond', 'Washington DC', 'Baltimore', 'Annapolis', 'Philadelphia',
        'Atlantic City', 'Cape May', 'Wildwood', 'Ocean City', 'Rehoboth Beach',
        'Lewes', 'Dover', 'Wilmington', 'Philadelphia', 'New York', 'Long Island',
        'Hamptons', 'Montauk', 'Fire Island', 'Jones Beach', 'Coney Island',
        'Brooklyn', 'Manhattan', 'Staten Island', 'Bronx', 'Queens', 'Westchester',
        'Hudson Valley', 'Catskills', 'Adirondacks', 'Lake Placid', 'Saratoga Springs',
        'Albany', 'Syracuse', 'Rochester', 'Buffalo', 'Niagara Falls', 'Erie',
        'Cleveland', 'Sandusky', 'Toledo', 'Detroit', 'Ann Arbor', 'Grand Rapids',
        'Traverse City', 'Mackinac Island', 'Sault Ste. Marie', 'Marquette',
        'Houghton', 'Duluth', 'Minneapolis', 'St. Paul', 'Rochester', 'Sioux Falls',
        'Rapid City', 'Mount Rushmore', 'Badlands', 'Custer', 'Deadwood', 'Sturgis',
        'Billings', 'Bozeman', 'Missoula', 'Helena', 'Great Falls', 'Glacier',
        'Kalispell', 'Whitefish', 'Coeur d\'Alene', 'Spokane', 'Seattle', 'Tacoma',
        'Olympia', 'Mount Rainier', 'Olympic', 'Port Angeles', 'Port Townsend',
        'San Juan Islands', 'Bellingham', 'Vancouver', 'Victoria', 'Portland',
        'Salem', 'Eugene', 'Bend', 'Crater Lake', 'Medford', 'Ashland', 'Grants Pass',
        'Redwood', 'Eureka', 'Mendocino', 'Fort Bragg', 'Ukiah', 'Santa Rosa',
        'Napa', 'Sonoma', 'Petaluma', 'San Francisco', 'Oakland', 'Berkeley',
        'Sausalito', 'Tiburon', 'Muir Woods', 'Point Reyes', 'Bodega Bay',
        'Santa Cruz', 'Monterey', 'Carmel', 'Big Sur', 'San Luis Obispo',
        'Pismo Beach', 'Santa Barbara', 'Ventura', 'Ojai', 'Los Angeles',
        'Hollywood', 'Beverly Hills', 'Santa Monica', 'Malibu', 'Long Beach',
        'Huntington Beach', 'Newport Beach', 'Laguna Beach', 'Dana Point',
        'San Clemente', 'Oceanside', 'Carlsbad', 'Encinitas', 'Del Mar',
        'La Jolla', 'San Diego', 'Coronado', 'Tijuana', 'Rosarito', 'Ensenada',
        'Palm Springs', 'Joshua Tree', 'Death Valley', 'Las Vegas', 'Hoover Dam',
        'Lake Mead', 'Valley of Fire', 'Zion', 'Bryce Canyon', 'Grand Canyon',
        'Antelope Canyon', 'Monument Valley', 'Arches', 'Canyonlands', 'Moab',
        'Capitol Reef', 'Goblin Valley', 'Salt Lake City', 'Park City', 'Provo',
        'Ogden', 'Logan', 'Yellowstone', 'Grand Teton', 'Jackson', 'Cody',
        'Sheridan', 'Cheyenne', 'Laramie', 'Fort Collins', 'Boulder', 'Denver',
        'Colorado Springs', 'Pueblo', 'Santa Fe', 'Taos', 'Albuquerque', 'Roswell',
        'Carlsbad Caverns', 'El Paso', 'Tucson', 'Phoenix', 'Scottsdale', 'Sedona',
        'Flagstaff', 'Grand Canyon', 'Lake Powell', 'Page', 'Monument Valley',
        'Moab', 'Arches', 'Canyonlands', 'Dead Horse Point', 'Capitol Reef',
        'Bryce Canyon', 'Zion', 'Las Vegas', 'Death Valley', 'Mammoth Lakes',
        'Yosemite', 'Lake Tahoe', 'Reno', 'Sacramento', 'San Francisco',
        'Napa Valley', 'Sonoma', 'Point Reyes', 'Bodega Bay', 'Mendocino',
        'Redwood', 'Eureka', 'Crescent City', 'Crater Lake', 'Bend', 'Portland',
        'Mount Hood', 'Columbia River Gorge', 'Mount St. Helens', 'Mount Rainier',
        'Olympic', 'Seattle', 'San Juan Islands', 'North Cascades', 'Winthrop',
        'Leavenworth', 'Spokane', 'Coeur d\'Alene', 'Missoula', 'Glacier',
        'Kalispell', 'Whitefish', 'Helena', 'Bozeman', 'Yellowstone', 'Grand Teton',
        'Jackson', 'Idaho Falls', 'Pocatello', 'Twin Falls', 'Boise', 'Sun Valley',
        'Ketchum', 'Stanley', 'McCall', 'Coeur d\'Alene', 'Spokane', 'Walla Walla',
        'Yakima', 'Ellensburg', 'Leavenworth', 'Wenatchee', 'Chelan', 'Winthrop',
        'North Cascades', 'Mount Baker', 'Bellingham', 'San Juan Islands', 'Seattle',
        'Tacoma', 'Olympia', 'Mount Rainier', 'Mount St. Helens', 'Columbia River Gorge',
        'Portland', 'Salem', 'Eugene', 'Bend', 'Crater Lake', 'Ashland', 'Medford',
        'Grants Pass', 'Redwood', 'Eureka', 'Arcata', 'Trinidad', 'Ferndale',
        'Fort Bragg', 'Mendocino', 'Point Arena', 'Gualala', 'Sea Ranch',
        'Bodega Bay', 'Point Reyes', 'Stinson Beach', 'Muir Beach', 'Sausalito',
        'San Francisco', 'Half Moon Bay', 'Pacifica', 'Santa Cruz', 'Capitola',
        'Monterey', 'Pacific Grove', 'Carmel', 'Big Sur', 'Cambria', 'San Simeon',
        'Hearst Castle', 'Morro Bay', 'Pismo Beach', 'San Luis Obispo', 'Solvang',
        'Santa Barbara', 'Ventura', 'Ojai', 'Malibu', 'Santa Monica', 'Los Angeles',
        'Long Beach', 'Huntington Beach', 'Newport Beach', 'Laguna Beach', 'San Diego'
    ]
    
    # Check if any common location is in the title
    for location in common_locations:
        if location.lower() in title.lower():
            return location
    
    # Common patterns in tour titles
    patterns = [
        r'in ([A-Za-z\s]+)',  # "Tour in Las Vegas"
        r'of ([A-Za-z\s]+)',  # "Tour of Las Vegas"
        r'to ([A-Za-z\s]+)',  # "Tour to Las Vegas"
        r'from ([A-Za-z\s]+)',  # "Tour from Las Vegas"
        r'^([A-Za-z\s]+) Tour',  # "Las Vegas Tour"
        r'^Private ([A-Za-z\s]+) Tour',  # "Private Las Vegas Tour"
    ]
    
    # Try to match patterns
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            location = match.group(1).strip()
            # Remove state name if it's a city
            location_parts = location.split(',')
            if len(location_parts) > 1:
                return location_parts[0].strip()
            return location
    
    # If no pattern matches, use a default approach
    # Split by common separators and take the first part
    separators = [',', ':', '-', '&', 'and', 'with']
    location = title
    for sep in separators:
        if sep in location:
            location = location.split(sep)[0].strip()
    
    # Remove common prefixes
    prefixes = ['Private', 'Tour', 'Guided', 'Day', 'Full-Day', 'Half-Day', 'Discover', 'Explore', 'Experience', 'Visit', 'See', 'Best of']
    for prefix in prefixes:
        if location.lower().startswith(prefix.lower()):
            location = location[len(prefix):].strip()
    
    # If location is too long, just use the first few words
    words = location.split()
    if len(words) > 3:
        location = ' '.join(words[:3])
    
    # If we still don't have a good location, use a default
    if len(location) < 3 or location.lower() in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
        return "this destination"
    
    return location

# Load the CSV data
def load_data():
    try:
        tours = []
        with open('Final-Viator-Tours.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean up data if needed
                for key in row:
                    if row[key] == '':
                        row[key] = None
                
                # Convert state abbreviation to full name
                if row['State'] and row['State'] in STATE_NAMES:
                    row['StateAbbr'] = row['State']  # Keep the abbreviation for reference
                    row['State'] = STATE_NAMES[row['State']]
                
                # Process the tour data
                processed_row = process_tour_data(row)
                tours.append(processed_row)
        return tours
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

# Global variables
tours_data = load_data()

# Get all states that have tours
def get_all_states():
    states = {}
    if tours_data:
        for tour in tours_data:
            if tour.get('StateAbbr') and tour.get('State'):
                states[tour['StateAbbr']] = tour['State']
        return [(abbr, name) for abbr, name in sorted(states.items(), key=lambda x: x[1])]
    return []

@app.route('/')
def home():
    states = get_all_states()
    west_coast_tours = get_west_coast_tours()
    east_coast_tours = get_east_coast_tours()
    most_reviewed_tours = get_most_reviewed_tours()
    return render_template('home.html', states=states, 
                          west_coast_tours=west_coast_tours,
                          east_coast_tours=east_coast_tours,
                          most_reviewed_tours=most_reviewed_tours,
                          now=datetime.now())

@app.route('/<state_name_lower>')
def state_tours(state_name_lower):
    states = get_all_states()
    west_coast_tours = get_west_coast_tours()
    east_coast_tours = get_east_coast_tours()
    most_reviewed_tours = get_most_reviewed_tours()
    
    # Get page number from query parameters, default to 1
    page = request.args.get('page', 1, type=int)
    
    # Replace hyphens with spaces for processing
    state_name_processed = state_name_lower.replace('-', ' ')
    
    # Convert lowercase state name to proper case
    state_full = STATE_NAMES_LOWER.get(state_name_processed.lower())
    
    # If not found in lowercase mapping, try other methods
    if not state_full:
        if state_name_processed.upper() in STATE_NAMES:
            # It's an abbreviation
            state_abbr = state_name_processed.upper()
            state_full = STATE_NAMES[state_abbr]
        else:
            # Try to capitalize the first letter of each word
            state_full = ' '.join(word.capitalize() for word in state_name_processed.split())
    
    # Get the abbreviation for the state
    state_abbr = STATE_ABBRS.get(state_full, state_name_processed.upper())
    
    # Filter tours by state
    state_tours = []
    for tour in tours_data:
        if (tour.get('StateAbbr') == state_abbr) or (tour.get('State') == state_full):
            state_tours.append(tour)
    
    # Sort tours by review count (descending)
    # Tours with no reviews will be at the end
    def get_review_count(tour):
        if tour.get('Reviews Count') and tour['Reviews Count'] > 0:
            return tour['Reviews Count']
        return 0
    
    state_tours.sort(key=get_review_count, reverse=True)
    
    # Pagination
    tours_per_page = 12
    total_tours = len(state_tours)
    total_pages = ceil(total_tours / tours_per_page)
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Get tours for the current page
    start_idx = (page - 1) * tours_per_page
    end_idx = start_idx + tours_per_page
    page_tours = state_tours[start_idx:end_idx]
    
    return render_template('state.html', 
        state=state_abbr, 
        state_full=state_full,
        tours=page_tours, 
        states=states,
        current_page=page,
        total_pages=total_pages,
        west_coast_tours=west_coast_tours,
        east_coast_tours=east_coast_tours,
        most_reviewed_tours=most_reviewed_tours,
        now=datetime.now()
    )

@app.route('/<state_name_lower>/tour/<tour_slug>')
def tour_detail(state_name_lower, tour_slug):
    states = get_all_states()
    west_coast_tours = get_west_coast_tours()
    east_coast_tours = get_east_coast_tours()
    most_reviewed_tours = get_most_reviewed_tours()
    
    # Replace hyphens with spaces for processing
    state_name_processed = state_name_lower.replace('-', ' ')
    
    # Convert lowercase state name to proper case
    state_full = STATE_NAMES_LOWER.get(state_name_processed.lower())
    
    # If not found in lowercase mapping, try other methods
    if not state_full:
        if state_name_processed.upper() in STATE_NAMES:
            # It's an abbreviation
            state_abbr = state_name_processed.upper()
            state_full = STATE_NAMES[state_abbr]
        else:
            # Try to capitalize the first letter of each word
            state_full = ' '.join(word.capitalize() for word in state_name_processed.split())
    
    # Get the abbreviation for the state
    state_abbr = STATE_ABBRS.get(state_full, state_name_processed.upper())
    
    # Find the tour by slug
    tour = None
    for t in tours_data:
        if t.get('Slug') == tour_slug:
            tour = t
            break
    
    # If tour not found, redirect to state page
    if not tour:
        return redirect(url_for('state_tours', state_name_lower=state_name_lower.lower()))
    
    # Filter tours by state
    state_tours = []
    for t in tours_data:
        if ((t.get('StateAbbr') == state_abbr) or (t.get('State') == state_full)) and t != tour:
            state_tours.append(t)
    
    # Make sure we have exactly 3 tours for the similar tours section
    # If we don't have enough tours from the same state, add some from other states
    if len(state_tours) < 3:  # We need exactly 3 similar tours
        other_states_tours = []
        for t in tours_data:
            if t != tour and t not in state_tours:
                other_states_tours.append(t)
        
        # Add some tours from other states
        random.shuffle(other_states_tours)
        state_tours.extend(other_states_tours[:3 - len(state_tours)])  # Add only what we need to reach 3
    
    # Limit to exactly 3 tours
    state_tours = state_tours[:3]
    
    return render_template('tour.html', 
                          tour=tour,
                          state=state_abbr, 
                          state_full=state_full, 
                          state_tours=state_tours,
                          states=states,
                          west_coast_tours=west_coast_tours,
                          east_coast_tours=east_coast_tours,
                          most_reviewed_tours=most_reviewed_tours,
                          now=datetime.now())

# Redirect old URLs to new format
@app.route('/state/<state_name_lower>')
def state_redirect(state_name_lower):
    return redirect(url_for('state_tours', state_name_lower=state_name_lower))

@app.route('/state/<state_name_lower>/tour/<int:tour_id>')
def tour_redirect_by_id(state_name_lower, tour_id):
    # Convert lowercase state name to proper case
    state_full = STATE_NAMES_LOWER.get(state_name_lower.lower())
    
    # If not found in lowercase mapping, try other methods
    if not state_full:
        if state_name_lower.upper() in STATE_NAMES:
            # It's an abbreviation
            state_abbr = state_name_lower.upper()
            state_full = STATE_NAMES[state_abbr]
        else:
            # Try to capitalize the first letter of each word
            state_full = ' '.join(word.capitalize() for word in state_name_lower.split())
    
    # Get the abbreviation for the state
    state_abbr = STATE_ABBRS.get(state_full, state_name_lower.upper())
    
    # Filter tours by state
    state_tours = []
    for tour in tours_data:
        if (tour.get('StateAbbr') == state_abbr) or (tour.get('State') == state_full):
            state_tours.append(tour)
    
    # Get the tour by ID
    if tour_id < len(state_tours):
        tour = state_tours[tour_id]
        # Redirect to the new URL format with slug
        return redirect(url_for('tour_detail', state_name_lower=state_name_lower, tour_slug=tour.get('Slug', f'tour-{tour_id}')))
    
    return redirect(url_for('state_tours', state_name_lower=state_name_lower))

@app.route('/search')
def search():
    states = get_all_states()
    west_coast_tours = get_west_coast_tours()
    east_coast_tours = get_east_coast_tours()
    most_reviewed_tours = get_most_reviewed_tours()
    query = request.args.get('query', '').lower()
    search_results = []
    
    if query:
        for tour in tours_data:
            # Safely get string values with defaults to prevent NoneType errors
            title = str(tour.get('Title', '') or '')
            description = str(tour.get('Description', '') or '')
            state = str(tour.get('State', '') or '')
            
            # Convert to lowercase for case-insensitive comparison
            title_lower = title.lower()
            description_lower = description.lower()
            state_lower = state.lower()
            
            if (query in title_lower or 
                query in description_lower or 
                query in state_lower):
                search_results.append(tour)
    
    return render_template('search.html', query=query, results=search_results, 
                          states=states, 
                          west_coast_tours=west_coast_tours,
                          east_coast_tours=east_coast_tours,
                          most_reviewed_tours=most_reviewed_tours,
                          now=datetime.now())

# Define west coast and east coast states
WEST_COAST_STATES = ['California', 'Oregon', 'Washington', 'Alaska', 'Hawaii', 'Nevada', 'Arizona']
EAST_COAST_STATES = ['Maine', 'New Hampshire', 'Massachusetts', 'Rhode Island', 'Connecticut', 'New York', 
                     'New Jersey', 'Delaware', 'Maryland', 'Virginia', 'North Carolina', 'South Carolina', 
                     'Georgia', 'Florida']

# Helper function to get west coast tours
def get_west_coast_tours(limit=5):
    west_coast_tours = []
    for tour in tours_data:
        if tour.get('State') in WEST_COAST_STATES:
            west_coast_tours.append(tour)
    
    # Shuffle and return limited number
    random.shuffle(west_coast_tours)
    return west_coast_tours[:limit]

# Helper function to get east coast tours
def get_east_coast_tours(limit=5):
    east_coast_tours = []
    for tour in tours_data:
        if tour.get('State') in EAST_COAST_STATES:
            east_coast_tours.append(tour)
    
    # Shuffle and return limited number
    random.shuffle(east_coast_tours)
    return east_coast_tours[:limit]

# Helper function to get most reviewed tours
def get_most_reviewed_tours(limit=5):
    # Create a copy of tours with reviews
    reviewed_tours = []
    for tour in tours_data:
        if tour.get('Reviews Count') and tour['Reviews Count'] > 0:
            reviewed_tours.append(tour)
    
    # Sort by review count (descending)
    reviewed_tours.sort(key=lambda x: x.get('Reviews Count', 0), reverse=True)
    return reviewed_tours[:limit]

@app.route('/sitemap')
def sitemap():
    states = get_all_states()
    west_coast_tours = get_west_coast_tours()
    east_coast_tours = get_east_coast_tours()
    most_reviewed_tours = get_most_reviewed_tours()
    
    # Get all tour categories
    tour_categories = set()
    for tour in tours_data:
        if tour.get('Type'):
            tour_categories.add(tour.get('Type'))
    
    # Sort categories alphabetically
    tour_categories = sorted(list(tour_categories))
    
    # Organize tours by state for the sitemap
    tours_by_state = {}
    for state_abbr, state_name in states:
        state_tours = []
        for tour in tours_data:
            if tour.get('StateAbbr') == state_abbr:
                state_tours.append(tour)
        tours_by_state[state_name] = state_tours
    
    return render_template('sitemap.html', 
                          states=states, 
                          tours_by_state=tours_by_state,
                          tour_categories=tour_categories,
                          west_coast_tours=west_coast_tours,
                          east_coast_tours=east_coast_tours,
                          most_reviewed_tours=most_reviewed_tours,
                          now=datetime.now())

if __name__ == '__main__':
    try:
        # Use threaded=True for better handling of multiple requests
        # Use processes=1 to avoid issues with the debugger
        app.run(debug=True, host='0.0.0.0', port=8083, threaded=True, processes=1)
    except Exception as e:
        print(f"Server error: {e}")
        # If there's an error, try to restart after a short delay
        import time
        time.sleep(2)
        print("Attempting to restart server...")
        app.run(debug=False, host='0.0.0.0', port=8083, threaded=True) 