import network
import urequests
import time
from machine import Pin, ADC, reset
import neopixel
import random
import math

# Globals
# WiFi credentials
SSID = 'aaaaaa'
PASSWORD = 'aaaaaaa'

PIXELS = 50

# Pin Assignment
ldr = ADC(26)  # LDR connected to ADC on GPIO 26
switch = Pin(15, Pin.IN, Pin.PULL_UP)  # Pull-up for momentary switch
np = neopixel.NeoPixel(Pin(28), PIXELS)
led = Pin("LED", Pin.OUT)


def trigger_bedtime(pin):
    global bedtime, np
    switch.irq(handler=None)  # Disable the interrupt after the first trigger we want the button to work once only per day
    print("Interrupt disabled")
    bedtime = True
    print('lights out')


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



# Calculate sleeps until Christmas
def sleeps_until_christmas(current_date):
    current_year = current_date[0]
    christmas_date = (current_year, 12, 25)
    christmas_struct = time.mktime(christmas_date + (0, 0, 0, 0, 0))
    today_struct = time.mktime(current_date + (0, 0, 0, 0, 0))
    sleeps = (christmas_struct - today_struct) // 86400 # seconds in a day
    return int(sleeps)


def clamp(value, min_val=0, max_val=255):
    # Clamp a value between min_val and max_val.
    return max(min(int(value), max_val), min_val)


def progress(np,sleeps, spread):
    advent = sleeps <= 24
    if advent:
        # Advent adjustment to progress bar
        # to make things confusing, LEDs are indexed from (PIXELS-1) to 0
        for i in range(24, sleeps-1, -1):
                variation_1 = (25-i) * random.choice ([-1,1]) #either -1 or +1, each sleep less is more volatile
                variation_2 = (25-i) * random.choice ([-1,1])
                pixelblockchunk = int(PIXELS/24) # We'll use blocks of this size for the first 23 days
                pixelblockmax = PIXELS - (24 - i) * pixelblockchunk
                if i>1:
                    pixelblockmin = pixelblockmax - pixelblockchunk
                else:
                    pixelblockmin = 0
                    # For Christmas Eve, use all remaining pixels
                # print(f'Day: {i}. {pixelblockmin} to {pixelblockmax}')
                for j in range(pixelblockmin,pixelblockmax):
                # Each block drifts at random, clamped between 0 and 255
                    r, g, b = np[j]  # The current RGB values of the pixel
                    r = clamp(r + variation_1)
                    g = clamp(g - variation_1)
                    b = clamp(b + variation_2)
                    np[j] =  (r,g,b)
    else:
        for i in range(PIXELS):
            # If it is not advent, then this formula will give a nice 'breathing' effect
            brightness = 32 * (1 + 4 *(math.sin(spread + math.pi)+1)) * math.exp(-(PIXELS/2-i) ** 2 / (1+20*(math.sin(spread)+1)) ** 2)
            np[i] =  ( clamp(todays_color_r * brightness), clamp(todays_color_g * brightness), clamp(todays_color_b * brightness))

    np.write()


def lightsout(np):
    for i in range(PIXELS):
        np[i] =  (0,0,0)
    np.write()


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
    

# Main program
def main():
    global bedtime, todays_color_r, todays_color_g, todays_color_b
    
    wake_up_routine(PIXELS)

    # Initialise local variables
    LDR_THRESHOLD = 700 # The light dependent resistor reading threshold for light/dark
    CONSECUTIVE_COUNT = 25 # Consecutive readings needed to count a reading as 'consistent
    consecutive_light_count = 0  # Counter for consecutive light readings below the threshold
    consecutive_dark_count = 0  # Counter for consecutive light readings below the threshold
    consistent_light = False
    consistent_dark = False
    spread = 0
    dark = False # Assume light
    bedtime = False  # Bedtime button not pressed
    twopi = math.pi*2
    
    #color of the day
    todays_color_r = random.randrange(1,99) /100
    todays_color_g = random.randrange(1,99) /100
    todays_color_b = random.randrange(1,99) /100
    print(f"today's based color: ({todays_color_r}, {todays_color_g}, {todays_color_b})")


    # Interrupts
    switch.irq(trigger=Pin.IRQ_FALLING, handler=trigger_bedtime)

    # Start
    # toggle onboard LED as sign of life
    led.on()       		# Turn the LED on
    time.sleep(0.5)     # Keep it on for 0.5 seconds
    led.off()      		# Turn the LED off
    lightsout(np) 		# Turn off the light strip lights
    connect_to_wifi(SSID, PASSWORD)
    # Get local time directly using IP

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

    # Calculate sleeps until Christmas
    sleeps = sleeps_until_christmas(current_date)
    print(f"Number of sleeps until Christmas: {sleeps}")
    # sleeps = 1
    # Main Loop
    while True:
        spread = (spread +.05) % twopi # The parameter that gets passed to progress for periodic light
        dark = ldr.read_u16() > LDR_THRESHOLD # True if ldr value is read as high
        if consistent_dark and not bedtime:  # Darkness detected
            progress(np,sleeps,spread)
        else:
            if bedtime or consistent_light:
                lightsout(np)

        if consistent_light and bedtime:
            # It has been light for multiple consecutive readings following a bedtime button press
            print('Looks like morning. Resetting...')
            reset()

        if dark:
            consecutive_light_count = 0  # Reset counter if reading goes above threshold
            consecutive_dark_count += 1
        else:
            consecutive_light_count += 1
            consecutive_dark_count = 0
        consistent_dark = consecutive_dark_count >= CONSECUTIVE_COUNT
        consistent_light = consecutive_light_count >= CONSECUTIVE_COUNT




# Run the main program
if __name__ == "__main__":
    main()
