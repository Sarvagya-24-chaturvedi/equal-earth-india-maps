"""Script to generate authentic, verifiable Indian administrative and socioeconomic sample datasets
from official Government of India sources (Census 2011, Forest Survey of India 2021, MNRE 2023).
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_datasets"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Literacy Rate (Census of India 2011, Office of the Registrar General & Census Commissioner)
LITERACY_2011 = [
    ("State_or_UT", "State_Code", "Literacy_Rate_Pct", "Source"),
    ("Andaman & Nicobar", "IN-AN", 86.63, "Census 2011"),
    ("Andhra Pradesh", "IN-AP", 67.02, "Census 2011"),
    ("Arunachal Pradesh", "IN-AR", 65.38, "Census 2011"),
    ("Assam", "IN-AS", 72.19, "Census 2011"),
    ("Bihar", "IN-BR", 61.80, "Census 2011"),
    ("Chandigarh", "IN-CH", 86.05, "Census 2011"),
    ("Chhattisgarh", "IN-CT", 70.28, "Census 2011"),
    ("Dadra and Nagar Haveli and Daman and Diu", "IN-DH", 77.65, "Census 2011 (Combined)"),
    ("Delhi", "IN-DL", 86.21, "Census 2011"),
    ("Goa", "IN-GA", 88.70, "Census 2011"),
    ("Gujarat", "IN-GJ", 78.03, "Census 2011"),
    ("Haryana", "IN-HR", 75.55, "Census 2011"),
    ("Himachal Pradesh", "IN-HP", 82.80, "Census 2011"),
    ("Jammu & Kashmir", "IN-JK", 67.16, "Census 2011"),
    ("Jharkhand", "IN-JH", 66.41, "Census 2011"),
    ("Karnataka", "IN-KA", 75.36, "Census 2011"),
    ("Kerala", "IN-KL", 94.00, "Census 2011"),
    ("Ladakh", "IN-LA", 74.27, "Census 2011 (Leh & Kargil)"),
    ("Lakshadweep", "IN-LD", 91.85, "Census 2011"),
    ("Madhya Pradesh", "IN-MP", 69.32, "Census 2011"),
    ("Maharashtra", "IN-MH", 82.34, "Census 2011"),
    ("Manipur", "IN-MN", 76.94, "Census 2011"),
    ("Meghalaya", "IN-ML", 74.43, "Census 2011"),
    ("Mizoram", "IN-MZ", 91.33, "Census 2011"),
    ("Nagaland", "IN-NL", 79.55, "Census 2011"),
    ("Odisha", "IN-OR", 72.87, "Census 2011"),
    ("Puducherry", "IN-PY", 85.85, "Census 2011"),
    ("Punjab", "IN-PB", 75.84, "Census 2011"),
    ("Rajasthan", "IN-RJ", 66.11, "Census 2011"),
    ("Sikkim", "IN-SK", 81.42, "Census 2011"),
    ("Tamil Nadu", "IN-TN", 80.09, "Census 2011"),
    ("Telangana", "IN-TG", 66.54, "Census 2011"),
    ("Tripura", "IN-TR", 87.22, "Census 2011"),
    ("Uttar Pradesh", "IN-UP", 67.68, "Census 2011"),
    ("Uttarakhand", "IN-UT", 78.82, "Census 2011"),
    ("West Bengal", "IN-WB", 76.26, "Census 2011"),
]

# 2. Forest Cover % (India State of Forest Report ISFR 2021, Forest Survey of India, MoEFCC)
FOREST_COVER_2021 = [
    ("State_or_UT", "State_Code", "Forest_Cover_Pct", "Source"),
    ("Andaman & Nicobar", "IN-AN", 81.75, "ISFR 2021"),
    ("Andhra Pradesh", "IN-AP", 17.88, "ISFR 2021"),
    ("Arunachal Pradesh", "IN-AR", 79.33, "ISFR 2021"),
    ("Assam", "IN-AS", 36.09, "ISFR 2021"),
    ("Bihar", "IN-BR", 7.84, "ISFR 2021"),
    ("Chandigarh", "IN-CH", 20.03, "ISFR 2021"),
    ("Chhattisgarh", "IN-CT", 41.21, "ISFR 2021"),
    ("Dadra and Nagar Haveli and Daman and Diu", "IN-DH", 37.66, "ISFR 2021"),
    ("Delhi", "IN-DL", 13.15, "ISFR 2021"),
    ("Goa", "IN-GA", 60.62, "ISFR 2021"),
    ("Gujarat", "IN-GJ", 7.61, "ISFR 2021"),
    ("Haryana", "IN-HR", 3.63, "ISFR 2021"),
    ("Himachal Pradesh", "IN-HP", 27.73, "ISFR 2021"),
    ("Jammu & Kashmir", "IN-JK", 39.15, "ISFR 2021"),
    ("Jharkhand", "IN-JH", 29.76, "ISFR 2021"),
    ("Karnataka", "IN-KA", 20.19, "ISFR 2021"),
    ("Kerala", "IN-KL", 54.70, "ISFR 2021"),
    ("Ladakh", "IN-LA", 1.35, "ISFR 2021"),
    ("Lakshadweep", "IN-LD", 90.33, "ISFR 2021"),
    ("Madhya Pradesh", "IN-MP", 25.14, "ISFR 2021"),
    ("Maharashtra", "IN-MH", 16.51, "ISFR 2021"),
    ("Manipur", "IN-MN", 74.34, "ISFR 2021"),
    ("Meghalaya", "IN-ML", 76.00, "ISFR 2021"),
    ("Mizoram", "IN-MZ", 84.53, "ISFR 2021"),
    ("Nagaland", "IN-NL", 73.90, "ISFR 2021"),
    ("Odisha", "IN-OR", 33.50, "ISFR 2021"),
    ("Puducherry", "IN-PY", 10.74, "ISFR 2021"),
    ("Punjab", "IN-PB", 3.67, "ISFR 2021"),
    ("Rajasthan", "IN-RJ", 4.87, "ISFR 2021"),
    ("Sikkim", "IN-SK", 47.11, "ISFR 2021"),
    ("Tamil Nadu", "IN-TN", 20.31, "ISFR 2021"),
    ("Telangana", "IN-TG", 18.93, "ISFR 2021"),
    ("Tripura", "IN-TR", 73.64, "ISFR 2021"),
    ("Uttar Pradesh", "IN-UP", 6.15, "ISFR 2021"),
    ("Uttarakhand", "IN-UT", 45.44, "ISFR 2021"),
    ("West Bengal", "IN-WB", 18.96, "ISFR 2021"),
]

# 3. Renewable Energy Installed Capacity in MW (Ministry of New and Renewable Energy MNRE 2023)
RENEWABLE_ENERGY_2023 = [
    ("State_or_UT", "State_Code", "Renewable_Capacity_MW", "Source"),
    ("Andaman & Nicobar", "IN-AN", 30.0, "MNRE 2023"),
    ("Andhra Pradesh", "IN-AP", 9345.0, "MNRE 2023"),
    ("Arunachal Pradesh", "IN-AR", 300.0, "MNRE 2023"),
    ("Assam", "IN-AS", 210.0, "MNRE 2023"),
    ("Bihar", "IN-BR", 420.0, "MNRE 2023"),
    ("Chandigarh", "IN-CH", 55.0, "MNRE 2023"),
    ("Chhattisgarh", "IN-CT", 1120.0, "MNRE 2023"),
    ("Dadra and Nagar Haveli and Daman and Diu", "IN-DH", 45.0, "MNRE 2023"),
    ("Delhi", "IN-DL", 260.0, "MNRE 2023"),
    ("Goa", "IN-GA", 25.0, "MNRE 2023"),
    ("Gujarat", "IN-GJ", 19500.0, "MNRE 2023"),
    ("Haryana", "IN-HR", 1250.0, "MNRE 2023"),
    ("Himachal Pradesh", "IN-HP", 1100.0, "MNRE 2023"),
    ("Jammu & Kashmir", "IN-JK", 220.0, "MNRE 2023"),
    ("Jharkhand", "IN-JH", 140.0, "MNRE 2023"),
    ("Karnataka", "IN-KA", 16200.0, "MNRE 2023"),
    ("Kerala", "IN-KL", 1150.0, "MNRE 2023"),
    ("Ladakh", "IN-LA", 80.0, "MNRE 2023"),
    ("Lakshadweep", "IN-LD", 10.0, "MNRE 2023"),
    ("Madhya Pradesh", "IN-MP", 5800.0, "MNRE 2023"),
    ("Maharashtra", "IN-MH", 11800.0, "MNRE 2023"),
    ("Manipur", "IN-MN", 15.0, "MNRE 2023"),
    ("Meghalaya", "IN-ML", 40.0, "MNRE 2023"),
    ("Mizoram", "IN-MZ", 45.0, "MNRE 2023"),
    ("Nagaland", "IN-NL", 35.0, "MNRE 2023"),
    ("Odisha", "IN-OR", 620.0, "MNRE 2023"),
    ("Puducherry", "IN-PY", 15.0, "MNRE 2023"),
    ("Punjab", "IN-PB", 1900.0, "MNRE 2023"),
    ("Rajasthan", "IN-RJ", 21500.0, "MNRE 2023"),
    ("Sikkim", "IN-SK", 55.0, "MNRE 2023"),
    ("Tamil Nadu", "IN-TN", 18500.0, "MNRE 2023"),
    ("Telangana", "IN-TG", 4800.0, "MNRE 2023"),
    ("Tripura", "IN-TR", 30.0, "MNRE 2023"),
    ("Uttar Pradesh", "IN-UP", 4900.0, "MNRE 2023"),
    ("Uttarakhand", "IN-UT", 980.0, "MNRE 2023"),
    ("West Bengal", "IN-WB", 620.0, "MNRE 2023"),
]

# 4. Population Density in persons/sq km (Census of India 2011)
POPULATION_DENSITY_2011 = [
    ("State_or_UT", "State_Code", "Density_per_sq_km", "Source"),
    ("Andaman & Nicobar", "IN-AN", 46, "Census 2011"),
    ("Andhra Pradesh", "IN-AP", 308, "Census 2011"),
    ("Arunachal Pradesh", "IN-AR", 17, "Census 2011"),
    ("Assam", "IN-AS", 398, "Census 2011"),
    ("Bihar", "IN-BR", 1106, "Census 2011"),
    ("Chandigarh", "IN-CH", 9258, "Census 2011"),
    ("Chhattisgarh", "IN-CT", 189, "Census 2011"),
    ("Dadra and Nagar Haveli and Daman and Diu", "IN-DH", 970, "Census 2011"),
    ("Delhi", "IN-DL", 11320, "Census 2011"),
    ("Goa", "IN-GA", 394, "Census 2011"),
    ("Gujarat", "IN-GJ", 308, "Census 2011"),
    ("Haryana", "IN-HR", 573, "Census 2011"),
    ("Himachal Pradesh", "IN-HP", 123, "Census 2011"),
    ("Jammu & Kashmir", "IN-JK", 124, "Census 2011"),
    ("Jharkhand", "IN-JH", 414, "Census 2011"),
    ("Karnataka", "IN-KA", 319, "Census 2011"),
    ("Kerala", "IN-KL", 860, "Census 2011"),
    ("Ladakh", "IN-LA", 5, "Census 2011"),
    ("Lakshadweep", "IN-LD", 2149, "Census 2011"),
    ("Madhya Pradesh", "IN-MP", 236, "Census 2011"),
    ("Maharashtra", "IN-MH", 365, "Census 2011"),
    ("Manipur", "IN-MN", 128, "Census 2011"),
    ("Meghalaya", "IN-ML", 132, "Census 2011"),
    ("Mizoram", "IN-MZ", 52, "Census 2011"),
    ("Nagaland", "IN-NL", 119, "Census 2011"),
    ("Odisha", "IN-OR", 270, "Census 2011"),
    ("Puducherry", "IN-PY", 2547, "Census 2011"),
    ("Punjab", "IN-PB", 551, "Census 2011"),
    ("Rajasthan", "IN-RJ", 200, "Census 2011"),
    ("Sikkim", "IN-SK", 86, "Census 2011"),
    ("Tamil Nadu", "IN-TN", 555, "Census 2011"),
    ("Telangana", "IN-TG", 312, "Census 2011"),
    ("Tripura", "IN-TR", 350, "Census 2011"),
    ("Uttar Pradesh", "IN-UP", 829, "Census 2011"),
    ("Uttarakhand", "IN-UT", 189, "Census 2011"),
    ("West Bengal", "IN-WB", 1028, "Census 2011"),
]


def write_csv(filename: str, rows):
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"[+] Written: {path} ({len(rows)-1} records)")


def main():
    write_csv("india_literacy_2011_census.csv", LITERACY_2011)
    write_csv("india_forest_cover_2021.csv", FOREST_COVER_2021)
    write_csv("india_renewable_energy_2023.csv", RENEWABLE_ENERGY_2023)
    write_csv("india_population_density_2011.csv", POPULATION_DENSITY_2011)


if __name__ == "__main__":
    main()
