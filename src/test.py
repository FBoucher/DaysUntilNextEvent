import machine, neopixel, time
from machine import Pin

PIXELS = 50
np = neopixel.NeoPixel(Pin(28), PIXELS)


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
    wake_up_routine(PIXELS)
    

# Run the main program
if __name__ == "__main__":
    main()