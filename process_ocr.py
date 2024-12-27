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

# def process_multiple_images_to_excel(image_paths):
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "OCR Results"

#     alignment = Alignment(horizontal="center", vertical="center")
#     yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#     red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

#     current_row = 1  

#     # Danh sách lưu lại các đường dẫn output
#     all_out_paths = []
#     title_results = [] 

#     for image_path in image_paths:
#         ocr_results, out_path ,title_result = process_image_with_coordinates(image_path, process_image(image_path))

#         # Thêm đường dẫn kết quả vào danh sách
#         all_out_paths.append(out_path)
#         title_results.append(title_result)

#         # Xác định khoảng ngưỡng để gom nhóm hàng/cột
#         threshold = 10

#         # Lấy tất cả tọa độ X và Y từ kết quả OCR
#         x_coords = [result['coordinates'][0] for result in ocr_results]
#         y_coords = [result['coordinates'][1] for result in ocr_results]

#         # Gom nhóm các tọa độ vào hàng và cột
#         x_groups = group_coordinates(x_coords, threshold)
#         y_groups = group_coordinates(y_coords, threshold)

#         # Xác định số hàng và số cột
#         max_row = len(y_groups)
#         max_col = len(x_groups)

#         # Tạo một ma trận trống để lưu các ô
#         matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

#         # Chèn các ô OCR vào ma trận
#         for result in ocr_results:
#             coords = result['coordinates']
#             x, y = coords[0], coords[1]

#             # Tìm cột gần nhất
#             col = min(range(len(x_groups)), key=lambda i: abs(x - x_groups[i]))
#             # Tìm hàng gần nhất
#             row = min(range(len(y_groups)), key=lambda i: abs(y - y_groups[i]))

#             # Ghi dữ liệu vào ma trận
#             matrix[row][col] = {
#                 "text": result["text"],
#                 "confidence": result["confidence"]
#             }

#         valid_matrix = [row for row in matrix if is_row_valid(row, max_col)]

#         # Ghi dữ liệu ma trận đã lọc vào Excel, loại bỏ các cột C (3), D (4), và F (6)
#         for row_idx, row_data in enumerate(valid_matrix, start=current_row):
#             col_idx = 1  # Cột bắt đầu từ 1 (A)

#             for cell_data in row_data:
#                 # Bỏ qua cột C (3), D (4), và F (6)
#                 if col_idx == 3:  # Cột C
#                     col_idx += 1
#                     continue
#                 elif col_idx == 4:  # Cột D
#                     col_idx += 1
#                     continue
#                 elif col_idx == 6:  # Cột F
#                     col_idx += 1
#                     continue

#                 if cell_data:  # Nếu ô có dữ liệu
#                     text = cell_data["text"]
#                     confidence = cell_data["confidence"]

#                     if col_idx == 2: 
#                         text = text.replace('O', '0')

#                     cell = ws.cell(row=row_idx, column=col_idx, value=text)
#                     cell.alignment = alignment

#                     if confidence < 0.5:
#                         cell.fill = red_fill
#                     elif confidence < 0.85:
#                         cell.fill = yellow_fill
#                 else:  
#                     ws.cell(row=row_idx, column=col_idx, value="")

#                 col_idx += 1  

#         current_row += len(valid_matrix)

#     os.makedirs("results_excel", exist_ok=True)

#     random_filename = f"OCR_Results_{uuid.uuid4().hex}.xlsx"
#     output_file = os.path.join("results_excel", random_filename)

#     wb.save(output_file)

#     return output_file, random_filename, all_out_paths, title_results
def convert_to_float(value):
    value = value.strip()
    
    value = value.replace(',', '.')
    if '-' in value:
        value = value.replace('-', '.') if not value.startswith('-') else value

    # Định nghĩa bảng thay thế ký tự
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

        # Chỉ trả về giá trị hợp lệ trong phạm vi [0, 10]
        if 0 <= numeric_value <= 10:
            return numeric_value
        else:
            return None
    except ValueError:
        # Trả về None nếu không chuyển đổi được
        return None
def process_multiple_images_to_groups(image_paths):
    all_grouped_data = []
    title_results = []
    out_paths = []  # Thêm danh sách này

    for image_path in image_paths:
        # Xử lý ảnh và lấy đường dẫn đầu ra
        ocr_results, out_path, title_result = process_image_with_coordinates(image_path, process_image(image_path))
        
        # Lưu đường dẫn đầu ra
        out_paths.append(out_path)  # Thêm đường dẫn đầu ra vào danh sách

        # Lưu kết quả tiêu đề
        title_results.append(title_result)

        # Tiếp tục xử lý nhóm dữ liệu...
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
