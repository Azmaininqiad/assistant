import cv2
import json

def draw_bounding_boxes(image_path, bounding_boxes):
    image = cv2.imread(image_path)

    for box in bounding_boxes:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, box["text"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Image with Bounding Boxes", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
bounding_boxes = [
    {"text": "Submit", "x": 100, "y": 200, "w": 80, "h": 30},  # Example Gemini output
]
draw_bounding_boxes("screenshot.png", bounding_boxes)
