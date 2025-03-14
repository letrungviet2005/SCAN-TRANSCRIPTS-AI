import os
import uuid
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill
from table_recognition.main import process_image
from character_recognition.intmain import process_image_with_coordinates

def group_coordinates(coordinates, threshold):
    grouped = []
    for coord in sorted(coordinates):
        if not grouped or coord - grouped[-1] > threshold:
            grouped.append(coord)
    return grouped

def is_row_valid(row_data, max_col, empty_threshold=0.07):
    filled_cells = sum(1 for cell in row_data if cell)  
    empty_cells = len(row_data) - filled_cells
    return (empty_cells / max_col) < empty_threshold  

def convert_to_float(value):
    value = value.strip()
    
    value = value.replace(',', '.')
    if '-' in value:
        value = value.replace('-', '.') if not value.startswith('-') else value

    
    replacements = {
    'O': '0', 'o': '0', 'Q': '0', 'D': '0',  
    'I': '1', 'l': '1', '|': '1', '/': '1', '\\': '1', 'A': '1', 'T': '1',  
    'Z': '2', 'z': '2', 'R': '2',  
    'E': '3', 'e': '3', '€': '3',  
    'h': '4', 'H': '4', '#': '4',  
    'S': '5', 's': '5', '$': '5',  
    'b': '6', 'G': '6', 'g': '6', 'q': '6',  
    'L': '7', 'T': '7', 'J': '7',  
    'B': '8', '&': '8', '8': '8',  
    'P': '9', 'g': '9', 'q': '9',  
}

    fixed_value = ''.join(replacements.get(c, c) for c in value)

    try:
        numeric_value = float(fixed_value)

        if numeric_value < 0 or numeric_value > 10:
            if len(fixed_value) == 2:
                numeric_value = numeric_value / 10
            elif len(fixed_value) == 3:
                numeric_value = numeric_value / 100

        if 0 <= numeric_value <= 10:
            return numeric_value
        else:
            return None
    except ValueError:
        return None
def process_multiple_images_to_groups(image_paths):
    all_grouped_data = []
    title_results = []
    out_paths = []  
    for image_path in image_paths:
        ocr_results, out_path, title_result = process_image_with_coordinates(image_path, process_image(image_path))
        
        out_paths.append(out_path) 

        title_results.append(title_result)

        threshold = 10
        y_coords = [result['coordinates'][1] for result in ocr_results]
        y_groups = group_coordinates(y_coords, threshold)
        grouped_data = [[] for _ in range(len(y_groups))]

        for result in ocr_results:
            coords = result['coordinates']
            y = coords[1]
            row_idx = min(range(len(y_groups)), key=lambda i: abs(y - y_groups[i]))
            grouped_data[row_idx].append({
                "text": result["text"],
                "confidence": result["confidence"],
                "sort_key": coords[0],
            })

        if grouped_data:
            max_row_length = max(len(row) for row in grouped_data)
        else:
            max_row_length = 0 
        valid_grouped_data = []

        for row in grouped_data:
            if len(row) < (max_row_length * 0.9 ):  
                continue

            if row and isinstance(row[0]["sort_key"], int) and row[0]["sort_key"] > 0:
                row_sorted = sorted(row, key=lambda cell: cell["sort_key"])
                first_text = row_sorted[0]["text"]

                if first_text.isdigit() and int(first_text) > 0:
                    indices_to_remove = [0, 2, 3, 5]
                    row_sorted = [cell for i, cell in enumerate(row_sorted) if i not in indices_to_remove]

                    if len(row_sorted) > 1:
                        element_1 = row_sorted[1]["text"]
                        element_1_value = convert_to_float(element_1)
                        if element_1_value is not None:
                            total_after_1 = sum(
                                convert_to_float(cell["text"]) for cell in row_sorted[2:]
                                if convert_to_float(cell["text"]) is not None
                            )
                            comparison_result = (total_after_1 == element_1_value)
                            for cell in row_sorted:
                                converted_value = convert_to_float(cell["text"])
                                if converted_value is not None:
                                    cell["text"] = str(converted_value)
                                cell["is_match"] = comparison_result

                        row_sorted = row_sorted[:2]

                    valid_grouped_data.append([{
                        "text": cell["text"],
                        "confidence": cell["confidence"],
                        "is_match": cell.get("is_match", None),
                    } for cell in row_sorted])

        all_grouped_data.append(valid_grouped_data)

    return all_grouped_data, title_results, out_paths
