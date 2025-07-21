import sys
import libs.hakosim as hakosim


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <config_path> <request_id>")
        return 1

    request_id = int(sys.argv[2])
    client = hakosim.MultirotorClient(sys.argv[1], "Drone")
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    client.vehicles["Drone"].camera_cmd_request_id = request_id

    #image_display_thread(client)
    png_image = client.simGetImage("0", hakosim.ImageType.Scene)
    if png_image:
        print("Image received successfully")
        with open("scene.png", "wb") as f:
            f.write(png_image)
    else:
        print("Failed to receive image")
    return 0

if __name__ == "__main__":
    sys.exit(main())
