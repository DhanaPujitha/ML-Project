import sys
from adjust import save_obj  # Adjust according to the actual function used
from hw import load_obj  # Adjust according to the actual function used

def generate_handwritten_text(handwriting_image_path, text_file_path, output_path):
    # Process the handwriting style image
    save_obj(handwriting_image_path)
    
    # Convert text to handwritten text using the processed style
    load_obj(text_file_path, output_path)

if __name__ == '__main__':
    handwriting_image_path = sys.argv[1]
    text_file_path = sys.argv[2]
    output_path = sys.argv[3]
    
    generate_handwritten_text(handwriting_image_path, text_file_path, output_path)
