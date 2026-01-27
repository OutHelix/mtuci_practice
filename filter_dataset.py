import os
import glob

old_to_new = {
    28: 0,  # dog -> 0
    20: 1   # cat -> 1
}

def convert_annotation_file(txt_path):
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        
        old_cls = int(parts[0])
        if old_cls in old_to_new:
            new_cls = old_to_new[old_cls]
            new_line = f"{new_cls} " + " ".join(parts[1:]) + "\n"
            new_lines.append(new_line)
    
    with open(txt_path, 'w') as f:
        f.writelines(new_lines)
    
    return len(new_lines)

def find_image_file(base_name, images_dir):
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
    for ext in img_extensions:
        img_path = os.path.join(images_dir, base_name + ext)
        if os.path.exists(img_path):
            return img_path
    return None

def process_dataset():
    splits = ['train', 'valid', 'test']
    
    for split in splits:
        label_dir = f'dataset/{split}/labels'
        images_dir = f'dataset/{split}/images'
        
        if not os.path.exists(label_dir):
            continue
        
        txt_files = glob.glob(os.path.join(label_dir, '*.txt'))
        total_files = len(txt_files)
        
        if total_files == 0:
            print(f"No txt files found")
            continue
        
        processed = 0
        removed_files = 0
        
        for txt_file in txt_files:
            base_name = os.path.basename(txt_file).replace('.txt', '')
            img_path = find_image_file(base_name, images_dir)
            
            annotations_count = convert_annotation_file(txt_file)
            
            if annotations_count == 0:
                os.remove(txt_file)
                
                if img_path and os.path.exists(img_path):
                    os.remove(img_path)
                
                removed_files += 1
            
            processed += 1
            if processed % 100 == 0:
                print(f"Processed {processed}/{total_files} files")
        
        remaining_txt = len(glob.glob(os.path.join(label_dir, '*.txt')))
        remaining_images = 0
        if os.path.exists(images_dir):
            img_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
            for ext in img_extensions:
                remaining_images += len(glob.glob(os.path.join(images_dir, f'*{ext}')))

if __name__ == "__main__":
    process_dataset()