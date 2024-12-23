import cv2
import numpy as np
from table_recognition.table_recognition import TableRecognizer, Table, Cell  # Import your TableRecognizer class


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
    """
    Xử lý hình ảnh và trả về danh sách các tọa độ dạng [x1, y1, x2, y2].

    :param file_path: Đường dẫn đến file hình ảnh cần xử lý.
    :param table_list: Danh sách các bảng (nếu cần sử dụng trước khi xử lý).
    :return: Danh sách tọa độ các bảng và các ô trong bảng.
    """
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

        # Chỉnh sửa ảnh nếu bảng bị thiếu cạnh
        for table in tables:
            image = add_borders_to_table(image, table)

        # Tiến hành nhận diện lại sau khi sửa ảnh
        tables: list[Table] = table_recognizer.process(image, table_list)

        # Chuẩn bị danh sách tọa độ trả về
        coordinates = []
        for table in tables:
            # Thêm tọa độ của bảng
            coordinates.append([table.xmin, table.ymin, table.xmax, table.ymax])
            # Thêm tọa độ các ô trong bảng
            for cell in table.cells:
                coordinates.append([cell.xmin, cell.ymin, cell.xmax, cell.ymax])

        return coordinates

    except Exception as e:
        raise RuntimeError(f"Error during processing: {e}")
