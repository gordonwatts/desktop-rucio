# Main program to run the certification
from src.grid.cert import cert

if __name__ == '__main__':
    c = cert()
    c.run_registration_loop()
