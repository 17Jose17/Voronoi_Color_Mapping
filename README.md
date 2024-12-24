# Voronoi Regions Visualization with Income Data

## Project Overview
This repository visualizes **Voronoi regions** on an interactive map, where each region is colored based on the income data of various branches. The data is loaded from a CSV file containing the geographic coordinates and income information of different branches, which were extracted from government data in Mexico City (CDMX). The points are transformed for correct geographic mapping, and a C++ code is used from Python to compute the Voronoi regions.

### Key Features:
- **Data Loading:** Load branch data from a CSV file extracted from government data (CDMX).
- **Point Transformation:** The geographic points are transformed for proper visualization on the map.
- **Voronoi Region Computation:** Voronoi regions are computed using a C++ code from Python.
- **Income-based Coloring:** Each Voronoi region is colored according to the income data of the corresponding branch.
- **Interactive Visualization:** The results are visualized on an interactive map using Folium.

## Methodology
### 1. Data Loading:
The branch data is loaded from a CSV file containing the following columns:
- **Latitude**: Geographic latitude of the branch.
- **Longitude**: Geographic longitude of the branch.
- **Income**: Income value associated with the branch.

### 2. Point Transformation:
The geographic points (latitude and longitude) are transformed for proper positioning and visualization on the map. Each pair of coordinates is flipped to align with the correct axes.

### 3. Voronoi Region Computation:
The Voronoi regions are computed using a C++ algorithm, which is executed through Python using a system call. This algorithm calculates the nearest regions based on the branch locations.

### 4. Income-based Coloring:
The Voronoi regions are colored based on the income data of the branches within each region, creating a visual representation of income distribution across the map.

### 5. Visualization:
The resulting regions and markers are visualized on an interactive map using the **Folium** library, allowing for zooming and panning to explore the geographic distribution of income.

https://e865d56c-9374-492b-bd7b-c5b7d39e9675-00-prwbkdkcgdw3.janeway.replit.dev/

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
