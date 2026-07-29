import cv2
import numpy as np

from table_recognition.table_recognition import Cell, Table, TableRecognizer


def is_image_file(file_path: str) -> bool:
    """Check whether the path points to a valid image file."""
    valid_extensions = [".png", ".jpeg", ".jpg"]
    return any(file_path.lower().endswith(ext) for ext in valid_extensions)


def add_borders_to_table(image: np.ndarray, table: Table) -> np.ndarray:
    """Draw borders around a detected table."""
    cv2.line(image, (table.xmin, table.ymin), (table.xmin, table.ymax), (0, 0, 0), 2)
    cv2.line(image, (table.xmax, table.ymin), (table.xmax, table.ymax), (0, 0, 0), 2)
    cv2.line(image, (table.xmin, table.ymin), (table.xmax, table.ymin), (0, 0, 0), 2)
    cv2.line(image, (table.xmin, table.ymax), (table.xmax, table.ymax), (0, 0, 0), 2)
    return image


def process_image(file_path: str, table_list: list = None) -> list[list[int]]:
    try:
        if not is_image_file(file_path):
            raise ValueError("Unsupported file format. Only PNG, JPEG, JPG are supported.")

        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Cannot read the image file. Check the file path.")

        table_recognizer: TableRecognizer = TableRecognizer.get_unique_instance()
        tables: list[Table] = table_recognizer.process(image, table_list)

        for table in tables:
            image = add_borders_to_table(image, table)

        tables: list[Table] = table_recognizer.process(image, table_list)

        coordinates = []
        for table in tables:
            for cell in table.cells:
                coordinates.append([cell.xmin, cell.ymin, cell.xmax, cell.ymax])

        return coordinates
    except Exception as exc:
        raise RuntimeError(f"Error during processing: {exc}") from exc
