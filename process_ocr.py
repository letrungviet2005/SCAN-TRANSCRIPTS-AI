import os
import uuid
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill
from table_recognition.main import process_image
from character_recognition.intmain import process_image_with_coordinates

# Hàm gom nhóm tọa độ
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

def process_multiple_images_to_excel(image_paths):
    wb = Workbook()
    ws = wb.active
    ws.title = "OCR Results"

    alignment = Alignment(horizontal="center", vertical="center")
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

    current_row = 1  

    # Danh sách lưu lại các đường dẫn output
    all_out_paths = []
    title_results = [] 

    for image_path in image_paths:
        ocr_results, out_path ,title_result = process_image_with_coordinates(image_path, process_image(image_path))

        # Thêm đường dẫn kết quả vào danh sách
        all_out_paths.append(out_path)
        title_results.append(title_result)

        # Xác định khoảng ngưỡng để gom nhóm hàng/cột
        threshold = 10

        # Lấy tất cả tọa độ X và Y từ kết quả OCR
        x_coords = [result['coordinates'][0] for result in ocr_results]
        y_coords = [result['coordinates'][1] for result in ocr_results]

        # Gom nhóm các tọa độ vào hàng và cột
        x_groups = group_coordinates(x_coords, threshold)
        y_groups = group_coordinates(y_coords, threshold)

        # Xác định số hàng và số cột
        max_row = len(y_groups)
        max_col = len(x_groups)

        # Tạo một ma trận trống để lưu các ô
        matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

        # Chèn các ô OCR vào ma trận
        for result in ocr_results:
            coords = result['coordinates']
            x, y = coords[0], coords[1]

            # Tìm cột gần nhất
            col = min(range(len(x_groups)), key=lambda i: abs(x - x_groups[i]))
            # Tìm hàng gần nhất
            row = min(range(len(y_groups)), key=lambda i: abs(y - y_groups[i]))

            # Ghi dữ liệu vào ma trận
            matrix[row][col] = {
                "text": result["text"],
                "confidence": result["confidence"]
            }

        # Lọc bỏ các hàng không hợp lệ
        valid_matrix = [row for row in matrix if is_row_valid(row, max_col)]

        # Ghi dữ liệu ma trận đã lọc vào Excel, loại bỏ các cột C (3), D (4), và F (6)
        for row_idx, row_data in enumerate(valid_matrix, start=current_row):
            col_idx = 1  # Cột bắt đầu từ 1 (A)

            for cell_data in row_data:
                # Bỏ qua cột C (3), D (4), và F (6)
                if col_idx == 3:  # Cột C
                    col_idx += 1
                    continue
                elif col_idx == 4:  # Cột D
                    col_idx += 1
                    continue
                elif col_idx == 6:  # Cột F
                    col_idx += 1
                    continue

                if cell_data:  # Nếu ô có dữ liệu
                    text = cell_data["text"]
                    confidence = cell_data["confidence"]

                    # Nếu là cột B (cột thứ 2), thay thế chữ 'O' bằng '0'
                    if col_idx == 2:  # Cột B (tính từ 1)
                        text = text.replace('O', '0')

                    cell = ws.cell(row=row_idx, column=col_idx, value=text)
                    cell.alignment = alignment

                    if confidence < 0.5:
                        cell.fill = red_fill
                    elif confidence < 0.85:
                        cell.fill = yellow_fill
                    
                else:  # Nếu ô trống
                    ws.cell(row=row_idx, column=col_idx, value="")

                col_idx += 1  # Tiến tới cột tiếp theo

        # Thêm khoảng trống giữa các ảnh
        current_row += len(valid_matrix)

    # Tạo thư mục lưu kết quả nếu chưa có
    os.makedirs("results_excel", exist_ok=True)

    # Tạo tên file ngẫu nhiên
    random_filename = f"OCR_Results_{uuid.uuid4().hex}.xlsx"
    output_file = os.path.join("results_excel", random_filename)

    # Lưu workbook vào file
    wb.save(output_file)

    return output_file, random_filename, all_out_paths, title_results
def convert_to_float(value):
    # Loại bỏ khoảng trắng ở đầu và cuối chuỗi
    value = value.strip()
    
    value = value.replace(',', '.')
    if '-' in value:
        value = value.replace('-', '.') if not value.startswith('-') else value

    # Định nghĩa bảng thay thế ký tự
    replacements = {
        'O': '0', 'o': '0', 'I': '1', 'l': '1', 
        'S': '5', 'B': '8', 'g': '9', 's': '5', 
        'b': '8', 'G': '9'
    }

    fixed_value = ''.join(replacements.get(c, c) for c in value)

    try:
        # Chuyển đổi giá trị chuỗi thành số thực
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

    for image_path in image_paths:
        # Xử lý OCR và tọa độ
        ocr_results, out_path, title_result = process_image_with_coordinates(image_path, process_image(image_path))

        # Lưu kết quả tiêu đề
        title_results.append(title_result)

        # Ngưỡng để gom nhóm hàng/cột
        threshold = 10

        # Lấy tất cả tọa độ Y từ kết quả OCR
        y_coords = [result['coordinates'][1] for result in ocr_results]

        # Gom nhóm các tọa độ Y vào các hàng
        y_groups = group_coordinates(y_coords, threshold)

        # Khởi tạo danh sách lưu các hàng
        grouped_data = [[] for _ in range(len(y_groups))]

        # Ghi dữ liệu OCR vào các hàng tương ứng
        for result in ocr_results:
            coords = result['coordinates']
            y = coords[1]

            # Tìm hàng gần nhất
            row_idx = min(range(len(y_groups)), key=lambda i: abs(y - y_groups[i]))

            grouped_data[row_idx].append({
                "text": result["text"],
                "confidence": result["confidence"],
                "sort_key": coords[0],
            })

        # Lọc và nhóm dữ liệu hợp lệ
        valid_grouped_data = []
        for row in grouped_data:
            if row and isinstance(row[0]["sort_key"], int) and row[0]["sort_key"] > 0:
                row_sorted = sorted(row, key=lambda cell: cell["sort_key"])

                first_text = row_sorted[0]["text"]
                if first_text.isdigit() and int(first_text) > 0:
                    indices_to_remove = [0, 2, 3, 5]
                    row_sorted = [cell for i, cell in enumerate(row_sorted) if i not in indices_to_remove]

                    if len(row_sorted) > 1:  # Kiểm tra phải có ít nhất 2 phần tử
                        element_1 = row_sorted[1]["text"]
                        element_1_value = convert_to_float(element_1)

                        if element_1_value is not None:
                            total_after_1 = sum(
                                convert_to_float(cell["text"]) for cell in row_sorted[2:]
                                if convert_to_float(cell["text"]) is not None
                            )

                            comparison_result = (total_after_1 == element_1_value)

                            for cell in row_sorted:
                                # Chuyển đổi text thành float nếu có thể
                                converted_value = convert_to_float(cell["text"])
                                if converted_value is not None:
                                    cell["text"] = str(converted_value)

                                cell["is_match"] = comparison_result  # true hoặc false

                    valid_grouped_data.append([{
                        "text": cell["text"],
                        "confidence": cell["confidence"],
                        "is_match": cell.get("is_match", None),
                    } for cell in row_sorted])

        all_grouped_data.append(valid_grouped_data)

    return all_grouped_data, title_results, out_path