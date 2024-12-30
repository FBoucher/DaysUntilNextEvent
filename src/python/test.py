import machine, neopixel, time
import urequests
from machine import Pin

PIXELS = 320
np = neopixel.NeoPixel(Pin(28), PIXELS)
SETTINGSURL = "https://storagec4ut4vi4benae.blob.core.windows.net/fileuploads/mysettings.json"

# Online Settings
ImportantDate = "2025-09-18"
PrimaryRGBColor = (0, 100, 0)
SecondaryRGBColor = (0, 0, 100)


# Function to validate that the lightstrip is working
def wake_up_routine(pixels):
    for i in range(pixels):
        np[i] = (0, 255, 0)
        np.write()
        time.sleep_ms(25)

    time.sleep_ms(500)
    np.fill((155, 155, 0))
    np.write()

    time.sleep_ms(500)
    np.fill((0, 0, 255))
    np.write()

    time.sleep_ms(500)
    np.fill((0, 0, 0))
    np.write()
    
    
# Function to get lighSettings
def get_light_settings():
    try:
        print(f"Fetching online settings")
        response = urequests.get(SETTINGSURL)
        if response.status_code == 200:
            data = response.json()
            # Extract ImportantDate, PrimaryRGBColor, SecondaryRGBColor directly from the JSON response
            ImportantDate = data['ImportantDate']
            PrimaryRGBColor = data['PrimaryRGBColor']
            SecondaryRGBColor = data['SecondaryRGBColor']
            response.close()
            return (ImportantDate, PrimaryRGBColor, SecondaryRGBColor)
        else:
            print(f"Error fetching online settings: {response.status_code}")
            response.close()
            return None
    except Exception as e:
        print("Error retrieving online settings:", e)
        return None    


# Function to connect to WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())


# Function to get timezone using ip-api.com
def get_timezone():
    url = "http://ipwhois.app/json/"
    try:
        print("Fetching timezone from IP...")
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            timezone = data.get('timezone', None)
            response.close()
            if timezone:
                print(f"Detected timezone: {timezone}")
                return timezone
            else:
                print("Timezone not found in response.")
                return None
        else:
            print(f"Error fetching timezone: {response.status_code}")
            response.close()
            return None
    except Exception as e:
        print("Error retrieving timezone:", e)
        return None



# Function to get local time using timeapi.io
def get_local_time(timezone):
    url = f"https://timeapi.io/api/Time/current/zone?timeZone={timezone}"
    try:
        print(f"Fetching local time for timezone: {timezone}")
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Extract year, month, day directly from the JSON response
            year = data['year']
            month = data['month']
            day = data['day']
            response.close()
            return (year, month, day)
        else:
            print(f"Error fetching local time: {response.status_code}")
            response.close()
            return None
    except Exception as e:
        print("Error retrieving local time:", e)
        return None
    

# Main program
def main():
    wake_up_routine(PIXELS)

    # Get timezone from IP
    timezone = get_timezone()
    if timezone is None:
        print("Could not detect timezone.")
        return
    
    # Get local time using the detected timezone
    current_date = get_local_time(timezone)
    if current_date is None:
        print("Could not retrieve local time.")
        return

    print(f"Current local date: {current_date}")
    
    get_light_settings()
    print(f"Important Date: {ImportantDate}")
    print(f"Primary RGB Color: {PrimaryRGBColor")
    print(f"Secondary RGB Color: {SecondaryRGBColor}")
    

# Run the main program
if __name__ == "__main__":
    main()