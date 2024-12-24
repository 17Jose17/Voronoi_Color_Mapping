import pandas as pd
import requests
import json
import pyproj
import ctypes
import folium
from branca.colormap import LinearColormap
from shapely.ops import unary_union
from shapely.geometry import Polygon

archivo_json = "limite-de-las-alcaldas.json"

with open(archivo_json, 'r') as file:
    json_data = json.load(file)

geodetic = pyproj.CRS('EPSG:4326')
utm = pyproj.CRS('EPSG:32614')
transformer = pyproj.Transformer.from_crs(geodetic, utm, always_xy=True)
transformer_inv = pyproj.Transformer.from_crs(utm, geodetic, always_xy=True)

def transform_coordinates(lon, lat):
    x, y = transformer.transform(lon, lat)
    return x, y

def transform_coordinates_back(x, y):
    lon, lat = transformer_inv.transform(x, y)
    return lon, lat

sucursales = pd.read_csv("Ventas.csv")

sucursales.drop(columns=['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5'], inplace=True)

sucursales['UTM'] = sucursales['Polar'].apply(
    lambda coord: f"{transformer.transform(float(coord.split(',')[1]), float(coord.split(',')[0]))}"
)

suc = sucursales['UTM'].tolist()

with open(archivo_json, 'r') as file:
    json_data = json.load(file)

data = []

for feature in json_data['features']:
    municipio = feature['properties']['NOMGEO']
    coordenadas = feature['geometry']['coordinates']

    data.append({
        'municipio': municipio,
        'coordenadas': coordenadas
    })

df = pd.DataFrame(data)

def transform_municipio_coordinates(coordinates):
    transformed_coords = []
    for coord_list in coordinates:
        transformed_coord = [transform_coordinates(lon, lat) for lon, lat in coord_list]
        transformed_coords.append(transformed_coord)
    return transformed_coords

df['coordenadas_utm'] = df['coordenadas'].apply(transform_municipio_coordinates)

def create_polygon_from_coords(coords):
    polygons = []
    for coord_list in coords:
        try:
            polygon = Polygon(coord_list)
            if polygon.is_valid:
                polygons.append(polygon)
        except Exception as e:
            print(f"Error al crear polígono: {e}")
    return polygons

df['poligonos'] = df['coordenadas_utm'].apply(create_polygon_from_coords)
all_polygons = [polygon for polygons in df['poligonos'] for polygon in polygons]
united_polygon = unary_union(all_polygons)

coords = list(united_polygon.exterior.coords)

def split_list(data, sizes):
    result = []
    idx = 0
    
    for size in sizes:
        result.append(data[idx:idx + size])
        idx += size
        
    return result

Succ = [tuple(map(float, point.strip('()').split(', '))) for point in suc]

lib = ctypes.CDLL('./libsum_list.so')

lib.calculateVoronoi.argtypes = [
    ctypes.POINTER(ctypes.c_longdouble), ctypes.POINTER(ctypes.c_longdouble),
    ctypes.POINTER(ctypes.c_longdouble), ctypes.POINTER(ctypes.c_longdouble),
    ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_longdouble), ctypes.POINTER(ctypes.c_int)
]
lib.calculateVoronoi.restype = ctypes.c_int

P_x = [point[0] for point in coords]
P_y = [point[1] for point in coords]
V_x = [point[0] for point in Succ]
V_y = [point[1] for point in Succ]

list1_ctypes = (ctypes.c_longdouble * len(P_x))(*P_x)
list2_ctypes = (ctypes.c_longdouble * len(P_y))(*P_y)
list3_ctypes = (ctypes.c_longdouble * len(V_x))(*V_x)
list4_ctypes = (ctypes.c_longdouble * len(V_y))(*V_y)

max_result_size = 100000
result_ctypes = (ctypes.c_longdouble * max_result_size)()
tam_result = (ctypes.c_int * len(V_x))()

num_elements = lib.calculateVoronoi(list1_ctypes, list2_ctypes, list3_ctypes, list4_ctypes, len(P_x), len(V_x), result_ctypes, tam_result)

result = []
for i in range(0, num_elements, 2):
    result.append((result_ctypes[i], result_ctypes[i + 1]))

sublists = split_list(result, tam_result)

def transform_sublists_back(sublists):
    transformed_sublists = []
    for sublist in sublists:
        transformed_points = [transform_coordinates_back(x, y) for x, y in sublist]
        transformed_sublists.append(transformed_points)
    return transformed_sublists

def transform_Succ_back(Succ):
    transformed_Succ = [transform_coordinates_back(x, y) for x, y in Succ]
    return transformed_Succ

transformed_sublists = transform_sublists_back(sublists)
transformed_Succ = transform_Succ_back(Succ)

transformed_sublists = [
    [(lat, lon) for lon, lat in coords]
    for coords in transformed_sublists
]

m = folium.Map(location=[transformed_sublists[0][0][0], transformed_sublists[0][0][1]], zoom_start=10, tiles='CartoDB Voyager')

max_ingreso = max(sucursales['Ingresos'])
colormap = LinearColormap(colors=['red', 'green'], vmin=0, vmax=max_ingreso)

for point in transformed_Succ:
    folium.Marker(location=[point[1], point[0]], icon=folium.Icon(color='red'), icon_size=(1, 1)).add_to(m)

for i, coord in enumerate(transformed_sublists):
    ingreso = sucursales['Ingresos'].iloc[i]
    color = colormap(ingreso)
    folium.Polygon(locations=coord, color=color, fill=True, fill_color=color, fill_opacity=0.2).add_to(m)

for i, row in df.iterrows():
    coords = row['coordenadas']
    inverted_coords = [(lon, lat) for lat, lon in coords[0]]
    folium.PolyLine(
        locations=inverted_coords,
        color="blue",
        weight=2,
        dash_array="5, 5",
    ).add_to(m)

colormap.add_to(m)

m
