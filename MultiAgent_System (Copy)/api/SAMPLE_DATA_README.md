# Sample Data Generator

This directory contains a script to generate sample data for the Keywords API.

## Files

- `create_sample_data.py` - Main script to generate sample data
- `SAMPLE_DATA_README.md` - This documentation file

## What the script creates

The sample data generator creates realistic data for:

### 1. Domains (10 domains)
- Technology
- Health & Fitness
- Finance & Business
- Education
- Travel & Tourism
- Food & Cooking
- Home & Garden
- Entertainment
- Sports
- Fashion & Beauty

### 2. Niches (80+ niches)
Each domain has multiple niches. For example:
- Technology: Web Development, Mobile Apps, AI, Cybersecurity, etc.
- Health & Fitness: Weight Loss, Muscle Building, Yoga, Nutrition, etc.
- Finance & Business: Investing, Entrepreneurship, Personal Finance, etc.

### 3. Subniches (100+ subniches)
Each niche has multiple subniches. For example:
- Web Development: Frontend, Backend, Full Stack, WordPress, E-commerce
- Mobile Apps: iOS Development, Android Development, Cross-platform, etc.

### 4. Keywords (1000+ keywords)
Each subniche/niche gets multiple keywords with:
- Realistic prefixes (best, top, ultimate, etc.)
- Main keywords combining domain/niche/subniche names
- Realistic suffixes (guide, tutorial, tips, etc.)
- Random scan platforms (Google, Bing, YouTube, etc.)
- Random statistics (links scanned, new links, duplicates)
- Random statuses and configurations

## How to run

### Prerequisites
1. Make sure your database is set up and running
2. Ensure your `.env` file has the correct `DATABASE_URL`
3. Make sure all migrations have been applied

### Running the script

```bash
# Navigate to the api directory
cd api

# Run the script
python create_sample_data.py
```

### Expected output

```
🚀 Starting sample data creation...
📁 Creating domains...
  ✅ Created domain: Technology
  ✅ Created domain: Health & Fitness
  ✅ Created domain: Finance & Business
  ...
📂 Creating niches...
  ✅ Created niche: Web Development (Domain: Technology)
  ✅ Created niche: Mobile Apps (Domain: Technology)
  ...
📑 Creating subniches...
  ✅ Created subniche: Frontend (Niche: Web Development)
  ✅ Created subniche: Backend (Niche: Web Development)
  ...
🔑 Creating keywords...
  ✅ Created keyword: best Web Development Technology guide
  ✅ Created keyword: top Web Development Technology tutorial
  ...

🎉 Sample data creation completed!
📊 Summary:
  • Domains: 10
  • Niches: 80
  • Subniches: 100
  • Keywords: 1500

✅ All sample data has been successfully added to the database!
```

## Data Structure

The script creates a hierarchical structure:

```
Domain (e.g., Technology)
├── Niche (e.g., Web Development)
│   ├── Subniche (e.g., Frontend)
│   │   └── Keywords (e.g., "best Frontend Web Development guide")
│   ├── Subniche (e.g., Backend)
│   │   └── Keywords (e.g., "top Backend Web Development tutorial")
│   └── ...
└── Niche (e.g., Mobile Apps)
    └── ...
```

## Customization

You can modify the script to:

1. **Add more domains**: Edit the `SAMPLE_DOMAINS` list
2. **Add more niches**: Edit the `SAMPLE_NICHES` dictionary
3. **Add more subniches**: Edit the `SAMPLE_SUBNICHES` dictionary
4. **Change keyword generation**: Modify the `generate_sample_keywords()` function
5. **Add more prefixes/suffixes**: Edit `SAMPLE_PREFIXES` and `SAMPLE_SUFFIXES` lists

## Notes

- The script uses async/await for database operations
- All entities get proper UUIDs for created_by/updated_by fields
- Keywords have realistic random data for all fields
- The script handles both niches with and without subniches
- All relationships are properly maintained

## Troubleshooting

If you encounter errors:

1. **Database connection issues**: Check your `DATABASE_URL` in `.env`
2. **Import errors**: Make sure you're running from the correct directory
3. **Duplicate key errors**: The script will fail if data already exists (run once only)
4. **Permission errors**: Make sure the script has execute permissions

## Clean up

If you need to remove the sample data, you can:

1. Drop and recreate your database
2. Or manually delete records from the tables in this order:
   - `tbl_keywords`
   - `tbl_subniches`
   - `tbl_niches`
   - `tbl_domains` 