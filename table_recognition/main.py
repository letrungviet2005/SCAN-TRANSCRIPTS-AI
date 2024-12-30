import cv2
import numpy as np
from table_recognition.table_recognition import TableRecognizer, Table, Cell  


def is_image_file(file_path: str) -> bool:
    """
    Kiểm tra nếu đường dẫn chỉ tới một file hình ảnh hợp lệ (PNG, JPEG, JPG).
    """
    valid_extensions = [".png", ".jpeg", ".jpg"]
    return any(file_path.lower().endswith(ext) for ext in valid_extensions)

def add_borders_to_table(image: np.ndarray, table: Table) -> np.ndarray:
    """
    Vẽ 4 đường kẻ cho bảng theo tọa độ của bảng (xmin, xmax, ymin, ymax).
    """
    # Vẽ cạnh trái (dọc)
    cv2.line(image, (table.xmin, table.ymin), (table.xmin, table.ymax), (0, 0, 0), 2)

    # Vẽ cạnh phải (dọc)
    cv2.line(image, (table.xmax, table.ymin), (table.xmax, table.ymax), (0, 0, 0), 2)

    # Vẽ cạnh trên (ngang)
    cv2.line(image, (table.xmin, table.ymin), (table.xmax, table.ymin), (0, 0, 0), 2)

    # Vẽ cạnh dưới (ngang)
    cv2.line(image, (table.xmin, table.ymax), (table.xmax, table.ymax), (0, 0, 0), 2)

    return image

def process_image(file_path: str, table_list: list = None) -> list[list[int]]:

    # def group_and_filter_coordinates(coordinates):
    #     # Sắp xếp theo ymin
    #     coordinates.sort(key=lambda x: x[1])

    #     grouped_rows = []
    #     current_row = []
        
    #     for coord in coordinates:
    #         if not current_row or abs(coord[1] - current_row[-1][1]) <= 25:
    #             current_row.append(coord)
    #         else:
    #             grouped_rows.append(current_row)
    #             current_row = [coord]

    #     if current_row:
    #         grouped_rows.append(current_row)

    #     filtered_rows = []
    #     for row in grouped_rows:
    #         filtered_row = [cell for idx, cell in enumerate(row) if idx not in {6,8,9,11 }]
    #         filtered_rows.extend(filtered_row)

    #     return filtered_rows

    try:
        # Kiểm tra nếu file là ảnh hợp lệ
        if not is_image_file(file_path):
            raise ValueError("Unsupported file format. Only PNG, JPEG, JPG are supported.")

        # Đọc hình ảnh từ file
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Cannot read the image file. Check the file path.")

        # Khởi tạo TableRecognizer
        table_recognizer: TableRecognizer = TableRecognizer.get_unique_instance()

        # Nhận diện bảng và ô
        tables: list[Table] = table_recognizer.process(image, table_list)
        
        for table in tables:
            image = add_borders_to_table(image, table)

        tables: list[Table] = table_recognizer.process(image, table_list)

        coordinates = []
        for table in tables:
            for cell in table.cells:
                coordinates.append([cell.xmin, cell.ymin, cell.xmax, cell.ymax])


        # Áp dụng sắp xếp và lọc
        # processed_coordinates = group_and_filter_coordinates(coordinates)

        # print(f'Processed coordinates: {processed_coordinates}')

        return coordinates

    except Exception as e:
        raise RuntimeError(f"Error during processing: {e}")

