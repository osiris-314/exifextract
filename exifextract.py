#!/usr/bin/env python3
from PIL import Image
import piexif
import sys
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

def format_value(value):
    """Format values for better readability."""
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            return f"<{len(value)} bytes>"
    elif isinstance(value, tuple):
        return ' '.join(str(v) for v in value)
    return str(value)

def convert_to_decimal(degree_tuple):
    """Convert GPS tuple to decimal degrees."""
    degrees, minutes, seconds = degree_tuple
    return degrees[0] / degrees[1] + (minutes[0] / minutes[1] / 60.0) + (seconds[0] / seconds[1] / 3600.0)

def get_google_maps_url(latitude, longitude):
    """Generate Google Maps URL."""
    return f"https://www.google.com/maps?q={latitude},{longitude}"

def parse_gps_data(exif_dict):
    """Parse and convert GPS data to human-readable format."""
    gps_info = exif_dict.get('GPS', {})
    
    # Extract data from EXIF
    latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef, b'N').decode('utf-8')
    longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef, b'W').decode('utf-8')
    latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
    longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)
    altitude = gps_info.get(piexif.GPSIFD.GPSAltitude)
    time_stamp = gps_info.get(piexif.GPSIFD.GPSTimeStamp)
    speed_ref = gps_info.get(piexif.GPSIFD.GPSSpeedRef)
    speed = gps_info.get(piexif.GPSIFD.GPSSpeed)
    img_direction_ref = gps_info.get(piexif.GPSIFD.GPSImgDirectionRef)
    img_direction = gps_info.get(piexif.GPSIFD.GPSImgDirection)
    dest_bearing_ref = gps_info.get(piexif.GPSIFD.GPSDestBearingRef)
    dest_bearing = gps_info.get(piexif.GPSIFD.GPSDestBearing)
    date_stamp = gps_info.get(piexif.GPSIFD.GPSDateStamp)
    pos_error = gps_info.get(piexif.GPSIFD.GPSHPositioningError)

    if latitude and longitude:
        lat_decimal = convert_to_decimal(latitude)
        lon_decimal = convert_to_decimal(longitude)
        
        if latitude_ref == 'S':
            lat_decimal = -lat_decimal
        if longitude_ref == 'W':
            lon_decimal = -lon_decimal
        
        google_maps_url = get_google_maps_url(lat_decimal, lon_decimal)
        
        return {
            'Latitude': f"{Fore.LIGHTGREEN_EX}{lat_decimal:.6f} {latitude_ref}",
            'Longitude': f"{Fore.LIGHTGREEN_EX}{lon_decimal:.6f} {longitude_ref}",
            'Google Maps URL': f"{Fore.LIGHTGREEN_EX}{google_maps_url}",
            'Altitude': f"{Fore.LIGHTGREEN_EX}{altitude[0] / altitude[1]:.2f} meters" if altitude else "N/A",
            'TimeStamp': f"{Fore.WHITE}{format_value(time_stamp)}",
            'Speed': f"{Fore.WHITE}{speed[0] / speed[1]} {speed_ref.decode('utf-8')}" if speed and speed_ref else "N/A",
            'ImgDirection': f"{Fore.WHITE}{img_direction[0] / img_direction[1]} {img_direction_ref.decode('utf-8')}" if img_direction and img_direction_ref else "N/A",
            'DestBearing': f"{Fore.WHITE}{dest_bearing[0] / dest_bearing[1]} {dest_bearing_ref.decode('utf-8')}" if dest_bearing and dest_bearing_ref else "N/A",
            'DateStamp': f"{Fore.WHITE}{format_value(date_stamp)}",
            'PosError': f"{Fore.WHITE}{pos_error[0] / pos_error[1]} meters" if pos_error else "N/A"
        }
    return {
        'Latitude': "N/A",
        'Longitude': "N/A",
        'Google Maps URL': "N/A",
        'Altitude': "N/A",
        'TimeStamp': "N/A",
        'Speed': "N/A",
        'ImgDirection': "N/A",
        'DestBearing': "N/A",
        'DateStamp': "N/A",
        'PosError': "N/A"
    }

def print_section_header(header):
    """Print section header with formatting."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{header}")

def print_exif_data(exif_dict, ifd_name):
    """Print EXIF data with color and formatting."""
    if ifd_name not in exif_dict:
        print(f"{Fore.RED}{Style.BRIGHT}{ifd_name} EXIF Data: {Fore.YELLOW}No data found.")
        return

    print(f"{Fore.GREEN}{Style.BRIGHT}{ifd_name} EXIF Data:")
    for tag_id, value in exif_dict[ifd_name].items():
        tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get('name', tag_id)
        if tag_name == 'MakerNote':
            continue  # Skip MakerNote
        formatted_value = format_value(value)
        print(f"  {Fore.CYAN}{tag_name}: {Fore.WHITE}{formatted_value}")

def get_exif_data(image_path):
    try:
        # Open image file
        image = Image.open(image_path)
    except IOError as e:
        print(f"{Fore.RED}Unable to open image file: {e}")
        return

    # Get image format
    image_format = image.format
    print(f"{Fore.GREEN}Image format: {Fore.YELLOW}{image_format}")

    # Extract EXIF data if image is a JPEG
    if image_format in ['JPEG', 'JPG']:
        try:
            exif_data = image.info.get('exif')
            if exif_data:
                # Use piexif to parse the EXIF data
                exif_dict = piexif.load(exif_data)
                
                # Print General Info
                print_section_header("General Information")
                print_exif_data(exif_dict, '0th')

                # Print Camera Settings
                print_section_header("Camera Settings")
                print_exif_data(exif_dict, 'Exif')

                # Print GPS Data
                print_section_header("GPS Data")
                gps_data = parse_gps_data(exif_dict)
                for key, value in gps_data.items():
                    print(f"  {Fore.CYAN}{key}: {value}")

                # Print Interop Data
                print_section_header("Interop Data")
                print_exif_data(exif_dict, 'Interop')

                # Print 1st EXIF Data
                print_section_header("1st EXIF Data")
                print_exif_data(exif_dict, '1st')

                # Handle thumbnail data
                if 'thumbnail' in exif_dict:
                    print_section_header("Thumbnail Data")
                    print(f"{Fore.RED}Thumbnail data found, but it is not parsed due to its binary nature.")

            else:
                print(f"{Fore.RED}No EXIF data found.")
        except Exception as e:
            print(f"{Fore.RED}Error extracting EXIF data: {e}")

    elif image_format in ['PNG', 'TIFF', 'WEBP', 'BMP']:
        # Basic image information for non-JPEG formats
        print(f"{Fore.GREEN}Basic Information:")
        print(f"  {Fore.CYAN}Format: {image_format}")
        print(f"  {Fore.CYAN}Size: {image.size[0]} x {image.size[1]}")
        print(f"  {Fore.CYAN}Mode: {image.mode}")
        print(f"  {Fore.CYAN}Info: {format_value(image.info)}")
        
        # Note: EXIF data is typically only available in JPEGs
        print(f"{Fore.RED}EXIF data extraction is primarily supported for JPEG images. Other formats may not have EXIF data.")

    else:
        print(f"{Fore.RED}Unsupported image format: {image_format}. EXIF data extraction is only supported for JPEG images.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{Fore.RED}Usage: python script.py <image_path>")
    else:
        get_exif_data(sys.argv[1])