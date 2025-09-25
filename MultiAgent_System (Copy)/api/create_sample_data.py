#!/usr/bin/env python3
"""
Sample Data Generator for Keywords API

This script creates sample data for domains, niches, subniches, and keywords.
Run this script to populate your database with realistic sample data.

Usage:
    python create_sample_data.py
"""

import asyncio
import os
import random
import sys
import uuid
from typing import Any, Dict, List

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from api.core.database import async_session
from api.src.keywords.models import (
    Domain,
    Keyword,
    KeywordStatus,
    KeywordStatusRun,
    Niche,
    Subniche,
)

# Sample data definitions
SAMPLE_DOMAINS = [
    "Technology",
    "Health & Fitness",
    "Finance & Business",
    "Education",
    "Travel & Tourism",
    "Food & Cooking",
    "Home & Garden",
    "Entertainment",
    "Sports",
    "Fashion & Beauty",
]

SAMPLE_NICHES = {
    "Technology": [
        "Web Development",
        "Mobile Apps",
        "Artificial Intelligence",
        "Cybersecurity",
        "Cloud Computing",
        "Data Science",
        "Gaming",
        "IoT Devices",
    ],
    "Health & Fitness": [
        "Weight Loss",
        "Muscle Building",
        "Yoga & Meditation",
        "Nutrition",
        "Mental Health",
        "Cardio Training",
        "Supplements",
        "Wellness",
    ],
    "Finance & Business": [
        "Investing",
        "Entrepreneurship",
        "Personal Finance",
        "Cryptocurrency",
        "Real Estate",
        "Marketing",
        "E-commerce",
        "Stock Trading",
    ],
    "Education": [
        "Online Learning",
        "Language Learning",
        "Programming Courses",
        "Academic Tutoring",
        "Professional Development",
        "Homeschooling",
        "Test Preparation",
        "Skill Development",
    ],
    "Travel & Tourism": [
        "Budget Travel",
        "Luxury Travel",
        "Adventure Tourism",
        "Cultural Tourism",
        "Business Travel",
        "Family Vacations",
        "Solo Travel",
        "Eco Tourism",
    ],
    "Food & Cooking": [
        "Healthy Recipes",
        "Baking",
        "International Cuisine",
        "Meal Planning",
        "Food Photography",
        "Restaurant Reviews",
        "Wine & Beverages",
        "Food Delivery",
    ],
    "Home & Garden": [
        "Interior Design",
        "Gardening",
        "DIY Projects",
        "Home Improvement",
        "Furniture",
        "Landscaping",
        "Home Organization",
        "Smart Home",
    ],
    "Entertainment": [
        "Movies & TV Shows",
        "Music",
        "Books & Reading",
        "Podcasts",
        "Streaming Services",
        "Live Events",
        "Celebrity News",
    ],
    "Sports": [
        "Football",
        "Basketball",
        "Tennis",
        "Golf",
        "Running",
        "Fitness Training",
        "Olympic Sports",
        "Extreme Sports",
    ],
    "Fashion & Beauty": [
        "Fashion Trends",
        "Makeup Tutorials",
        "Skincare",
        "Hair Care",
        "Fashion Shopping",
        "Beauty Products",
        "Style Tips",
        "Sustainable Fashion",
    ],
}

SAMPLE_SUBNICHES = {
    "Web Development": ["Frontend", "Backend", "Full Stack", "WordPress", "E-commerce"],
    "Mobile Apps": [
        "iOS Development",
        "Android Development",
        "Cross-platform",
        "App Marketing",
        "App Design",
    ],
    "Artificial Intelligence": [
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "Computer Vision",
        "AI Ethics",
    ],
    "Cybersecurity": [
        "Network Security",
        "Application Security",
        "Penetration Testing",
        "Security Tools",
        "Threat Intelligence",
    ],
    "Cloud Computing": ["AWS", "Azure", "Google Cloud", "DevOps", "Serverless"],
    "Data Science": [
        "Data Analysis",
        "Data Visualization",
        "Big Data",
        "Statistics",
        "Predictive Analytics",
    ],
    "IoT Devices": [
        "Smart Home",
        "Wearables",
        "Industrial IoT",
        "IoT Security",
        "IoT Platforms",
    ],
    "Weight Loss": [
        "Diet Plans",
        "Exercise Routines",
        "Supplements",
        "Meal Prep",
        "Fitness Tracking",
    ],
    "Muscle Building": [
        "Strength Training",
        "Bodybuilding",
        "Nutrition",
        "Recovery",
        "Supplements",
    ],
    "Yoga & Meditation": [
        "Hatha Yoga",
        "Vinyasa",
        "Meditation Apps",
        "Mindfulness",
        "Stress Relief",
    ],
    "Nutrition": [
        "Healthy Eating",
        "Meal Planning",
        "Superfoods",
        "Dietary Supplements",
        "Food Allergies",
    ],
    "Mental Health": [
        "Anxiety Relief",
        "Depression Support",
        "Therapy",
        "Self-care",
        "Mindfulness",
    ],
    "Cardio Training": ["Running", "Cycling", "Swimming", "HIIT", "Endurance Training"],
    "Supplements": [
        "Protein",
        "Vitamins",
        "Pre-workout",
        "Post-workout",
        "Natural Supplements",
    ],
    "Wellness": [
        "Holistic Health",
        "Alternative Medicine",
        "Wellness Retreats",
        "Health Coaching",
        "Lifestyle Medicine",
    ],
    "Investing": [
        "Stock Market",
        "Real Estate",
        "Cryptocurrency",
        "Retirement Planning",
        "Portfolio Management",
    ],
    "Entrepreneurship": [
        "Startup Business",
        "Small Business",
        "Business Planning",
        "Funding",
        "Marketing",
    ],
    "Personal Finance": [
        "Budgeting",
        "Saving Money",
        "Debt Management",
        "Credit Cards",
        "Financial Planning",
    ],
    "Cryptocurrency": ["Bitcoin", "Ethereum", "Trading", "Mining", "DeFi"],
    "Real Estate": [
        "Buying Homes",
        "Selling Homes",
        "Rental Properties",
        "Real Estate Investment",
        "Property Management",
    ],
    "Marketing": [
        "Digital Marketing",
        "Social Media Marketing",
        "Content Marketing",
        "SEO",
        "Email Marketing",
    ],
    "E-commerce": [
        "Online Stores",
        "Dropshipping",
        "Amazon FBA",
        "Shopify",
        "E-commerce Marketing",
    ],
    "Stock Trading": [
        "Day Trading",
        "Swing Trading",
        "Options Trading",
        "Technical Analysis",
        "Trading Platforms",
    ],
}

# Sample keywords with prefixes and suffixes
SAMPLE_PREFIXES = [
    "best",
    "top",
    "ultimate",
    "complete",
    "essential",
    "advanced",
    "beginner",
    "professional",
    "affordable",
    "premium",
    "free",
    "cheap",
    "expensive",
    "quality",
    "reliable",
    "trusted",
    "popular",
    "trending",
    "viral",
    "famous",
    "expert",
    "certified",
    "licensed",
    "accredited",
    "modern",
    "traditional",
    "innovative",
    "classic",
    "contemporary",
    "vintage",
    "luxury",
    "budget",
]

SAMPLE_SUFFIXES = [
    "guide",
    "tutorial",
    "tips",
    "tricks",
    "strategies",
    "methods",
    "techniques",
    "approaches",
    "reviews",
    "comparison",
    "vs",
    "alternatives",
    "options",
    "solutions",
    "tools",
    "software",
    "courses",
    "training",
    "certification",
    "program",
    "plan",
    "system",
    "framework",
    "platform",
    "services",
    "providers",
    "companies",
    "brands",
    "products",
    "apps",
    "websites",
    "resources",
]

SAMPLE_SCAN_PLATFORMS = ["Youtube", "Website"]


def generate_sample_keywords(
    domain_name: str, niche_name: str, subniche_name: str = None
) -> List[Dict[str, Any]]:
    """Generate sample keywords for a given domain, niche, and subniche."""
    keywords = []
    used_keywords = set()  # Track used full_keywords to avoid duplicates

    # Base keyword combinations
    base_combinations = [
        (domain_name, niche_name),
        (niche_name, domain_name),
    ]

    if subniche_name:
        base_combinations.extend(
            [
                (subniche_name, niche_name),
                (niche_name, subniche_name),
                (domain_name, subniche_name),
                (subniche_name, domain_name),
            ]
        )

    # Additional keyword variations
    additional_keywords = [
        niche_name,
        domain_name,
    ]

    if subniche_name:
        additional_keywords.append(subniche_name)

    # Generate keywords for each combination
    for main_part, secondary_part in base_combinations:
        # Use all prefixes and suffixes to ensure variety and avoid duplicates
        for prefix in SAMPLE_PREFIXES[:6]:  # Use first 6 prefixes
            for suffix in SAMPLE_SUFFIXES[:4]:  # Use first 4 suffixes
                main_keyword = f"{main_part} {secondary_part}"
                full_keyword = f"{prefix} {main_keyword} {suffix}"

                # Skip if this keyword already exists
                if full_keyword in used_keywords:
                    continue

                used_keywords.add(full_keyword)

                keywords.append(
                    {
                        "prefix": prefix,
                        "main_keyword": main_keyword,
                        "suffix": suffix,
                        "full_keyword": full_keyword,
                        "scan_platform": random.choice(SAMPLE_SCAN_PLATFORMS),
                        "total_links_scanned": random.randint(100, 5000),
                        "total_links_new": random.randint(10, 500),
                        "total_links_dupicate": random.randint(5, 200),
                        "status": random.choice(
                            [KeywordStatus.ACTIVE, KeywordStatus.DEACTIVATED]
                        ),
                        "status_run": random.choice(
                            [
                                KeywordStatusRun.SUCCESS,
                                KeywordStatusRun.ERROR,
                                KeywordStatusRun.RUNNING,
                            ]
                        ),
                        "favorite": random.choice([True, False]),
                        "scheduler_config": {
                            "frequency": random.choice(["daily", "weekly", "monthly"]),
                            "enabled": random.choice([True, False]),
                        },
                    }
                )

    # Generate additional simple keywords without prefix/suffix
    for keyword_term in additional_keywords:
        for suffix in SAMPLE_SUFFIXES[:3]:  # Use first 3 suffixes
            full_keyword = f"{keyword_term} {suffix}"

            # Skip if this keyword already exists
            if full_keyword in used_keywords:
                continue

            used_keywords.add(full_keyword)

            keywords.append(
                {
                    "prefix": None,
                    "main_keyword": keyword_term,
                    "suffix": suffix,
                    "full_keyword": full_keyword,
                    "scan_platform": random.choice(SAMPLE_SCAN_PLATFORMS),
                    "total_links_scanned": random.randint(100, 5000),
                    "total_links_new": random.randint(10, 500),
                    "total_links_dupicate": random.randint(5, 200),
                    "status": random.choice(
                        [KeywordStatus.ACTIVE, KeywordStatus.DEACTIVATED]
                    ),
                    "status_run": random.choice(
                        [
                            KeywordStatusRun.SUCCESS,
                            KeywordStatusRun.ERROR,
                            KeywordStatusRun.RUNNING,
                        ]
                    ),
                    "favorite": random.choice([True, False]),
                    "scheduler_config": {
                        "frequency": random.choice(["daily", "weekly", "monthly"]),
                        "enabled": random.choice([True, False]),
                    },
                }
            )

    return keywords


async def create_sample_data():
    """Create sample data for all entities."""
    async with async_session() as session:
        print("🚀 Starting sample data creation...")

        # Global tracking for unique keywords across all domains
        global_used_keywords = set()

        # Create domains
        print("📁 Creating domains...")
        domains = {}
        for domain_name in SAMPLE_DOMAINS:
            domain = Domain(
                name=domain_name, created_by=uuid.uuid4(), updated_by=uuid.uuid4()
            )
            session.add(domain)
            await session.flush()  # Flush to get the ID
            domains[domain_name] = domain
            print(f"  ✅ Created domain: {domain_name}")

        # Create niches
        print("📂 Creating niches...")
        niches = {}
        for domain_name, niche_names in SAMPLE_NICHES.items():
            domain = domains[domain_name]
            for niche_name in niche_names:
                niche = Niche(
                    name=niche_name,
                    domain_id=domain.id,
                    created_by=uuid.uuid4(),
                    updated_by=uuid.uuid4(),
                )
                session.add(niche)
                await session.flush()
                niches[niche_name] = niche
                print(f"  ✅ Created niche: {niche_name} (Domain: {domain_name})")

        # Create subniches
        print("📑 Creating subniches...")
        subniches = {}
        for niche_name, subniche_names in SAMPLE_SUBNICHES.items():
            if niche_name in niches:
                niche = niches[niche_name]
                for subniche_name in subniche_names:
                    subniche = Subniche(
                        name=subniche_name,
                        niche_id=niche.id,
                        created_by=uuid.uuid4(),
                        updated_by=uuid.uuid4(),
                    )
                    session.add(subniche)
                    await session.flush()
                    subniches[subniche_name] = subniche
                    print(
                        f"  ✅ Created subniche: {subniche_name} (Niche: {niche_name})"
                    )

        # Create keywords
        print("🔑 Creating keywords...")
        keyword_count = 0

        for domain_name, niche_names in SAMPLE_NICHES.items():
            domain = domains[domain_name]

            for niche_name in niche_names:
                niche = niches[niche_name]

                # Get subniches for this niche
                niche_subniches = SAMPLE_SUBNICHES.get(niche_name, [])

                if niche_subniches:
                    # Create keywords for each subniche
                    for subniche_name in niche_subniches:
                        if subniche_name in subniches:
                            subniche = subniches[subniche_name]
                            sample_keywords = generate_sample_keywords(
                                domain_name, niche_name, subniche_name
                            )

                            for keyword_data in sample_keywords:
                                # Check global uniqueness
                                if keyword_data["full_keyword"] in global_used_keywords:
                                    continue

                                global_used_keywords.add(keyword_data["full_keyword"])

                                keyword = Keyword(
                                    **keyword_data,
                                    domain_id=domain.id,
                                    niche_id=niche.id,
                                    sub_niche_id=subniche.id,
                                    created_by=uuid.uuid4(),
                                    updated_by=uuid.uuid4(),
                                )
                                session.add(keyword)
                                keyword_count += 1
                else:
                    # Create keywords for niche without subniche
                    sample_keywords = generate_sample_keywords(domain_name, niche_name)

                    for keyword_data in sample_keywords:
                        # Check global uniqueness
                        if keyword_data["full_keyword"] in global_used_keywords:
                            continue

                        global_used_keywords.add(keyword_data["full_keyword"])

                        keyword = Keyword(
                            **keyword_data,
                            domain_id=domain.id,
                            niche_id=niche.id,
                            sub_niche_id=None,
                            created_by=uuid.uuid4(),
                            updated_by=uuid.uuid4(),
                        )
                        session.add(keyword)
                        keyword_count += 1

        # Commit all changes
        await session.commit()

        print(f"\n🎉 Sample data creation completed!")
        print(f"📊 Summary:")
        print(f"  • Domains: {len(domains)}")
        print(f"  • Niches: {len(niches)}")
        print(f"  • Subniches: {len(subniches)}")
        print(f"  • Keywords: {keyword_count}")
        print(f"\n✅ All sample data has been successfully added to the database!")


async def main():
    """Main function to run the sample data creation."""
    try:
        await create_sample_data()
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
