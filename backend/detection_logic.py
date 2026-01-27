import cv2
from ultralytics import YOLO

class AnimalDetector:
    def __init__(self, model_path="models/yolo11n.pt"):
        self.model = YOLO(model_path)
        
        self.target_classes = ['cat', 'dog']
        self.target_class_ids = []
        
        for class_id, class_name in self.model.names.items():
            if class_name.lower() in self.target_classes:
                self.target_class_ids.append(class_id)
    
    def detect_on_image(self, image_path, conf_threshold=0.25):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        height, width = img.shape[:2]
        
        # Detect only target classes
        results = self.model(img, conf=conf_threshold, classes=self.target_class_ids)
        
        detections = []
        stats = {
            'total_animals': 0,
            'cats': 0,
            'dogs': 0
        }
        
        # Process results
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    stats['total_animals'] += 1
                    class_name = self.model.names[cls_id].lower()
                    
                    if class_name == 'cat':
                        stats['cats'] += 1
                        color = (0, 165, 255)
                    elif class_name == 'dog':
                        stats['dogs'] += 1
                        color = (0, 255, 0)
                    else:
                        continue
                    
                    detections.append({
                        'class': class_name,
                        'confidence': round(conf, 3),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
                    
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    label = f"{class_name}: {conf:.2f}"
                    cv2.putText(img, label, (int(x1), int(y1) - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        stats_text = f"Animals: {stats['total_animals']} (Cats: {stats['cats']}, Dogs: {stats['dogs']})"
        cv2.putText(img, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        _, buffer = cv2.imencode('.jpg', img)
        result_image_bytes = buffer.tobytes()
        
        return {
            'detections': detections,
            'stats': stats,
            'result_image': result_image_bytes
        }